"""Real HTTP/ORM tests with fake import boundaries and per-test memory SQLite.

Never imports production app.database or app.services.ai_service. Run only this
tests directory, not legacy test_*.py files at the backend root.
"""

from contextlib import ExitStack
import importlib
import socket
import sys
import threading
from types import ModuleType
import unittest
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool


CSV = b"name,sales\nA,100\nB,200\nC,300\nD,400\n"
DATASET_FIELDS = {"id", "filename", "row_count", "column_count", "uploaded_at",
                  "status", "error_message", "updated_at"}
ANALYSIS_FIELDS = {"id", "dataset_id", "analysis", "insights", "ai_insight", "created_at"}
FAILURE = "数据分析失败，请稍后重新上传文件"


class APIBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Refuse a pre-imported application: isolation must precede its imports.
        guarded = ("app.main", "app.api.data", "app.database", "app.models.dataset",
                   "app.models.dataset_analysis", "app.services.ai_service",
                   "app.services.dataset_service")
        if any(name in sys.modules for name in guarded):
            raise RuntimeError("Run this baseline in a fresh Python process")
        cls.stack = ExitStack()
        cls.addClassCleanup(cls.stack.close)
        # Windows asyncio builds its wake-up socket pair through connect().
        # Permit only that standard-library operation on its own thread.
        local = threading.local()
        original_connect = socket.socket.connect
        original_socketpair = socket.socketpair
        def guarded_connect(sock, address):
            if not getattr(local, "building_socketpair", False):
                raise AssertionError("Network forbidden")
            return original_connect(sock, address)
        def internal_socketpair(*args, **kwargs):
            local.building_socketpair = True
            try:
                return original_socketpair(*args, **kwargs)
            finally:
                local.building_socketpair = False
        cls.stack.enter_context(patch("socket.socket.connect", new=guarded_connect))
        cls.stack.enter_context(patch("socket.socketpair", new=internal_socketpair))
        cls.stack.enter_context(patch("socket.create_connection", side_effect=AssertionError("Network forbidden")))
        database = ModuleType("app.database")
        database.Base = declarative_base()
        database.SessionLocal = Mock(side_effect=AssertionError("Unbound test database"))
        ai = ModuleType("app.services.ai_service")
        ai.generate_ai_insight = Mock(side_effect=AssertionError("Unmocked AI forbidden"))
        cls.stack.enter_context(patch.dict(sys.modules, {"app.database": database,
                                                       "app.services.ai_service": ai}))
        cls.main = importlib.import_module("app.main")
        cls.data = importlib.import_module("app.api.data")
        cls.service = importlib.import_module("app.services.dataset_service")
        cls.Dataset = importlib.import_module("app.models.dataset").Dataset
        cls.Analysis = importlib.import_module("app.models.dataset_analysis").DatasetAnalysis
        cls.Base = database.Base

    def setUp(self):
        self.engine = create_engine("sqlite://", poolclass=StaticPool,
                                    connect_args={"check_same_thread": False})
        self.addCleanup(self.engine.dispose)
        @event.listens_for(self.engine, "connect")
        def enable_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")
        self.Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.sessions = []

        def session_factory():
            session = self.Session()
            session.close = Mock(wraps=session.close)
            self.sessions.append(session)
            return session

        self.factory = self.enterContext(patch.object(self.service, "SessionLocal", side_effect=session_factory))
        self.ai = self.enterContext(patch.object(self.service, "generate_ai_insight", return_value="离线 AI 洞察"))
        self.logger = self.enterContext(patch.object(self.service, "logger"))
        self.enterContext(patch.object(self.data, "logger", self.logger))
        self.client = self.enterContext(TestClient(self.main.app, raise_server_exceptions=False))

    def tearDown(self):
        try:
            for session in self.sessions:
                self.assertEqual(session.close.call_count, 1)
        finally:
            for session in self.sessions:
                # Bypass the spy for emergency cleanup without masking assertions.
                type(session).close(session)

    def upload(self, path="/api/data/analyze", content=CSV, filename="baseline.csv"):
        return self.client.post(path, files={"file": (filename, content, "text/csv")})

    def counts(self):
        with self.Session() as db:
            return db.query(self.Dataset).count(), db.query(self.Analysis).count()

    def test_isolation_guards(self):
        self.assertEqual(self.engine.url.drivername, "sqlite")
        self.assertIs(self.service.Dataset.__table__.metadata, self.Base.metadata)
        self.assertFalse(hasattr(sys.modules["app.database"], "DATABASE_URL"))
        with socket.socket() as probe:
            with self.assertRaisesRegex(AssertionError, "Network forbidden"):
                probe.connect(("127.0.0.1", 3306))
        with self.assertRaisesRegex(AssertionError, "Network forbidden"):
            socket.create_connection(("127.0.0.1", 3306))
        with self.assertRaisesRegex(AssertionError, "Unmocked AI forbidden"):
            sys.modules["app.services.ai_service"].generate_ai_insight({})

    def test_route_inventory(self):
        # FastAPI may retain included routers as lazy registration containers.
        # Its generated schema resolves them into the effective HTTP paths.
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        routes = {(method.upper(), path)
                  for path, operations in response.json()["paths"].items()
                  for method in operations}
        self.assertEqual(routes, {
            ("GET", "/"), ("GET", "/api/health"), ("GET", "/api/data/datasets"),
            ("GET", "/api/data/datasets/{dataset_id}"),
            ("GET", "/api/data/datasets/{dataset_id}/analysis"),
            ("POST", "/api/data/analyze"), ("POST", "/api/data/ai-insight"),
            ("GET", "/api/data/analysis/count"), ("GET", "/api/data/quality"),
        })

    def test_root_health_and_cors(self):
        for path, body in [("/", {"message": "Welcome to DataInsightAI"}),
                           ("/api/health", {"status": "ok", "project": "DataInsightAI"})]:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), body)
        response = self.client.options("/api/data/analyze", headers={
            "Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["access-control-allow-origin"], "http://localhost:5173")
        self.assertEqual(response.headers["access-control-allow-credentials"], "true")
        self.factory.assert_not_called()
        self.ai.assert_not_called()

    def test_empty_reads_and_missing_records(self):
        for path, body in [("/api/data/datasets", []), ("/api/data/analysis/count", {"count": 0}),
                           ("/api/data/quality", {"quality_score": 0})]:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), body)
        for path, detail in [("/api/data/datasets/999", "数据集不存在"),
                             ("/api/data/datasets/999/analysis", "该数据集暂无分析结果")]:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json(), {"detail": detail})

    def test_parameter_validation_and_method(self):
        for path in ["/api/data/analyze", "/api/data/ai-insight"]:
            self.assertEqual(self.client.post(path).status_code, 422)
            self.assertEqual(self.client.get(path).status_code, 405)
        for suffix in ["", "/analysis"]:
            self.assertEqual(self.client.get("/api/data/datasets/not-int" + suffix).status_code, 422)
        self.factory.assert_not_called()
        self.ai.assert_not_called()

    def test_csv_errors_do_not_create_tasks(self):
        for path in ["/api/data/analyze", "/api/data/ai-insight"]:
            for content, filename, detail in [
                (CSV, "a.txt", "只支持 CSV 文件"), (b"", "a.csv", "上传的 CSV 文件为空"),
                (b"\xff", "a.csv", "CSV 文件编码不是 UTF-8"),
                (b"\n", "a.csv", "CSV 文件没有有效数据"),
                (b'a,b\n"unterminated', "a.csv", "CSV 文件格式错误，无法解析"),
            ]:
                with self.subTest(path=path, detail=detail):
                    response = self.upload(path, content, filename)
                    self.assertEqual(response.status_code, 400)
                    self.assertEqual(response.json(), {"detail": detail})
        self.factory.assert_not_called()
        self.ai.assert_not_called()
        self.assertEqual(self.counts(), (0, 0))

    def test_oversize_http_contract(self):
        for path in ["/api/data/analyze", "/api/data/ai-insight"]:
            # Service test covers actual 20MiB; keep HTTP fixtures small/in-memory.
            with patch("app.services.csv_loader.MAX_FILE_SIZE", 8):
                response = self.upload(path)
            self.assertEqual(response.status_code, 413)
            self.assertEqual(response.json(), {"detail": "上传的 CSV 文件不能超过 20MB"})
        self.factory.assert_not_called()
        self.ai.assert_not_called()

    def test_success_pending_visibility_and_persistence(self):
        def ai_result(analysis):
            self.assertEqual(analysis["rows"], 4)
            self.assertEqual(len(self.sessions), 1)
            self.sessions[0].close.assert_called_once_with()
            with self.Session() as db:
                self.assertEqual(db.query(self.Dataset).one().status, "pending")
                self.assertEqual(db.query(self.Analysis).count(), 0)
            return "离线 AI 洞察"
        self.ai.side_effect = ai_result
        response = self.upload()
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(set(body), {"filename", "analysis", "insights", "ai_insight", "dataset_id", "status"})
        self.assertEqual(body["status"], "completed")
        self.assertEqual(body["filename"], "baseline.csv")
        self.assertEqual(body["ai_insight"], "离线 AI 洞察")
        detail = self.client.get(f'/api/data/datasets/{body["dataset_id"]}').json()
        self.assertEqual(set(detail), DATASET_FIELDS)
        self.assertEqual((detail["row_count"], detail["column_count"]), (4, 2))
        self.assertEqual(detail["status"], "completed")
        self.assertIsNone(detail["error_message"])
        self.assertIsInstance(detail["uploaded_at"], str)
        self.assertIsInstance(detail["updated_at"], str)
        stored = self.client.get(f'/api/data/datasets/{body["dataset_id"]}/analysis').json()
        self.assertEqual(set(stored), ANALYSIS_FIELDS)
        for field in ["analysis", "insights", "ai_insight"]:
            self.assertEqual(stored[field], body[field])
        self.assertEqual(self.client.get("/api/data/datasets").json(), [detail])
        self.assertEqual(self.client.get("/api/data/analysis/count").json(), {"count": 1})
        self.assertEqual(self.client.get("/api/data/quality").json(), {"quality_score": 100.0})
        self.assertEqual(self.counts(), (1, 1))

    def test_ai_failure_marks_failed(self):
        self.ai.side_effect = RuntimeError("offline failure")
        response = self.upload()
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": FAILURE})
        self.assertEqual(self.counts(), (1, 0))
        item = self.client.get("/api/data/datasets").json()[0]
        self.assertEqual(item["status"], "failed")
        self.assertEqual(item["error_message"], FAILURE)
        self.assertEqual(self.client.get(f'/api/data/datasets/{item["id"]}').json(), item)
        self.assertEqual(self.client.get(f'/api/data/datasets/{item["id"]}/analysis').status_code, 404)

    def test_unique_value_counts_survive_json_persistence(self):
        response = self.upload(content=b"repeated,distinct,empty\nA,1,\nA,2,\nB,3,\n,4,\n")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        expected = {"repeated": 2, "distinct": 4, "empty": 0}
        self.assertEqual(body["analysis"]["unique_values"], expected)
        stored = self.client.get(f'/api/data/datasets/{body["dataset_id"]}/analysis')
        self.assertEqual(stored.status_code, 200)
        self.assertEqual(stored.json()["analysis"]["unique_values"], expected)
        self.assertNotIn("unique_counts", stored.json()["analysis"])

    def test_analysis_failure_marks_failed_without_ai(self):
        with patch.object(self.service, "analyze_dataframe", side_effect=RuntimeError("offline analysis")):
            response = self.upload()
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": FAILURE})
        self.assertEqual(self.counts(), (1, 0))
        self.assertEqual(self.client.get("/api/data/datasets").json()[0]["status"], "failed")
        self.ai.assert_not_called()

    def test_creation_commit_failure_rolls_back(self):
        session = self.Session()
        rollback = Mock(wraps=session.rollback)
        session.rollback = rollback
        session.close = Mock(wraps=session.close)
        session.commit = Mock(side_effect=RuntimeError("offline commit failure"))
        self.sessions.append(session)
        self.factory.side_effect = None
        self.factory.return_value = session
        response = self.upload()
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": "数据分析任务创建失败，请稍后重试"})
        rollback.assert_called_once_with()
        self.ai.assert_not_called()
        self.assertEqual(self.counts(), (0, 0))

    def test_final_commit_failure_rolls_back_then_marks_failed(self):
        original_factory = self.factory.side_effect
        rollback = Mock()
        def factory():
            session = original_factory()
            if len(self.sessions) == 2:
                session.commit = Mock(side_effect=RuntimeError("offline final commit failure"))
                rollback.side_effect = session.rollback
                session.rollback = rollback
            return session
        self.factory.side_effect = factory
        response = self.upload()
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": FAILURE})
        rollback.assert_called_once_with()
        self.assertEqual(self.counts(), (1, 0))
        self.assertEqual(self.client.get("/api/data/datasets").json()[0]["status"], "failed")

    def test_failure_marker_commit_failure_preserves_pending(self):
        original_factory = self.factory.side_effect
        def factory():
            session = original_factory()
            if len(self.sessions) == 2:
                session.commit = Mock(side_effect=RuntimeError("offline marker failure"))
            return session
        self.factory.side_effect = factory
        self.ai.side_effect = RuntimeError("offline AI failure")
        response = self.upload()
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": FAILURE})
        self.assertEqual(self.client.get("/api/data/datasets").json()[0]["status"], "pending")
        self.assertEqual(self.counts(), (1, 0))

    def test_ai_only_success_and_failure_never_persist(self):
        response = self.upload("/api/data/ai-insight")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"filename": "baseline.csv", "ai_insight": "离线 AI 洞察"})
        self.ai.side_effect = RuntimeError("offline failure")
        response = self.upload("/api/data/ai-insight")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": "AI 洞察生成过程中发生错误：offline failure"})
        self.factory.assert_not_called()
        self.assertEqual(self.counts(), (0, 0))

    def test_failed_marker_session_creation_keeps_original_error_mapping(self):
        original_factory = self.factory.side_effect
        def factory():
            if self.sessions:
                raise RuntimeError("offline failed-marker session creation")
            return original_factory()
        self.factory.side_effect = factory
        self.ai.side_effect = RuntimeError("offline AI failure")
        response = self.upload()
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": "数据分析任务创建失败，请稍后重试"})
        self.assertEqual(self.counts(), (1, 0))
        with self.Session() as db:
            self.assertEqual(db.query(self.Dataset).one().status, "pending")
        self.logger.exception.assert_any_call("创建 Dataset 分析任务失败")

    def test_completed_commit_is_atomic_and_releases_connection_before_ai(self):
        from sqlalchemy import inspect
        original_factory = self.factory.side_effect
        commits = []
        def factory():
            session = original_factory()
            original_commit = session.commit
            def commit():
                if len(self.sessions) == 1:
                    dataset = next(obj for obj in session.new if isinstance(obj, self.Dataset))
                    commits.append(("pending", dataset.status))
                else:
                    record = next(obj for obj in session.new if isinstance(obj, self.Analysis))
                    dataset = session.query(self.Dataset).filter(self.Dataset.id == record.dataset_id).one()
                    commits.append(("analysis", dataset.status))
                original_commit()
            session.commit = commit
            return session
        self.factory.side_effect = factory
        def ai_result(_):
            self.assertEqual(len(self.sessions), 1)
            self.assertFalse(self.sessions[0].in_transaction())
            self.sessions[0].close.assert_called_once_with()
            return "离线 AI 洞察"
        self.ai.side_effect = ai_result
        response = self.upload()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(commits, [("pending", "pending"), ("analysis", "completed")])
        record = self.service.get_dataset(response.json()["dataset_id"])
        self.assertTrue(inspect(record).detached)
        self.assertEqual(record.status, "completed")

    def test_failed_marker_rollback_and_logging(self):
        original_factory = self.factory.side_effect
        rollback = Mock()
        def factory():
            session = original_factory()
            if len(self.sessions) == 2:
                session.commit = Mock(side_effect=RuntimeError("offline marker failure"))
                rollback.side_effect = session.rollback
                session.rollback = rollback
            return session
        self.factory.side_effect = factory
        self.ai.side_effect = RuntimeError("offline AI failure")
        response = self.upload()
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": FAILURE})
        rollback.assert_called_once_with()
        with self.Session() as db:
            dataset = db.query(self.Dataset).one()
            self.assertEqual(dataset.status, "pending")
            self.logger.exception.assert_any_call("Dataset %s 分析失败", dataset.id)
            self.logger.exception.assert_any_call("更新 Dataset %s 失败状态时发生错误", dataset.id)

    def test_order_latest_analysis_and_quality_average(self):
        from datetime import datetime
        with self.Session() as db:
            old = self.Dataset(filename="old.csv", row_count=1, column_count=1,
                               status="pending", uploaded_at=datetime(2020, 1, 1))
            new = self.Dataset(filename="new.csv", row_count=1, column_count=1,
                               status="completed", uploaded_at=datetime(2021, 1, 1))
            db.add_all([old, new])
            db.flush()
            new_id = new.id
            for year, analysis in [(2020, {"quality_score": 80}),
                                   (2021, {"quality_score": "91.1"}), (2022, {})]:
                db.add(self.Analysis(dataset_id=new_id, analysis=analysis, insights={},
                                     ai_insight=str(year), created_at=datetime(year, 1, 1)))
            db.commit()
        response = self.client.get("/api/data/datasets")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["filename"] for item in response.json()], ["new.csv", "old.csv"])
        latest = self.client.get(f"/api/data/datasets/{new_id}/analysis")
        self.assertEqual(latest.status_code, 200)
        self.assertEqual(latest.json()["ai_insight"], "2022")
        self.assertEqual(self.client.get("/api/data/analysis/count").json(), {"count": 3})
        self.assertEqual(self.client.get("/api/data/quality").json(), {"quality_score": 85.5})

    def test_quality_no_scores_and_invalid_historical_score(self):
        with self.Session() as db:
            dataset = self.Dataset(filename="history.csv", row_count=0, column_count=1)
            db.add(dataset)
            db.flush()
            record = self.Analysis(dataset_id=dataset.id, analysis={}, insights={}, ai_insight="offline")
            db.add(record)
            db.commit()
            record_id = record.id
        self.assertEqual(self.client.get("/api/data/quality").json(), {"quality_score": 0})
        with self.Session() as db:
            db.get(self.Analysis, record_id).analysis = {"quality_score": "invalid"}
            db.commit()
        response = self.client.get("/api/data/quality")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.text, "Internal Server Error")


if __name__ == "__main__":
    unittest.main()
