from __future__ import annotations

from hashlib import sha256
from pathlib import Path

import pytest

from agent_context_gateway.aws_runtime import (
    DynamoContextSliceCache,
    DynamoSliceStore,
    S3ContextStore,
    validate_context_id,
)
from agent_context_gateway.models import ContextSlice, TaskRequest


class FakeS3:
    def __init__(self) -> None:
        self.objects = {
            "sources/team-a/service/prod/main.tf": b'resource "aws_s3_bucket" "example" {}',
            "sources/team-a/README.md": b"# Team A",
        }

    def list_objects_v2(self, **request):
        prefix = request["Prefix"]
        return {
            "Contents": [
                {
                    "Key": key,
                    "ETag": sha256(value).hexdigest(),
                    "Size": len(value),
                }
                for key, value in self.objects.items()
                if key.startswith(prefix)
            ],
            "IsTruncated": False,
        }

    def download_file(self, _bucket: str, key: str, destination: str) -> None:
        Path(destination).write_bytes(self.objects[key])


class FakeTable:
    def __init__(self) -> None:
        self.items = {}

    def get_item(self, *, Key, ConsistentRead):
        assert ConsistentRead is True
        item = self.items.get(Key["cache_key"])
        return {"Item": dict(item)} if item else {}

    def put_item(self, *, Item):
        self.items[Item["cache_key"]] = Item

    def update_item(self, *, Key, UpdateExpression, ExpressionAttributeValues):
        assert "ADD hits" in UpdateExpression
        item = self.items[Key["cache_key"]]
        item["hits"] += ExpressionAttributeValues[":one"]
        item["last_accessed_at"] = ExpressionAttributeValues[":now"]


class FakeSliceTable:
    def __init__(self) -> None:
        self.items = {}

    def get_item(self, *, Key, ConsistentRead):
        assert ConsistentRead is True
        item = self.items.get(Key["slice_id"])
        return {"Item": dict(item)} if item else {}

    def batch_writer(self, *, overwrite_by_pkeys):
        assert overwrite_by_pkeys == ["slice_id"]
        table = self

        class Writer:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return None

            def put_item(self, *, Item):
                table.items[Item["slice_id"]] = Item

        return Writer()


def test_s3_context_store_materializes_named_context() -> None:
    store = S3ContextStore("test-bucket", client=FakeS3())
    with store.materialize("team-a") as root:
        assert (root / "service/prod/main.tf").is_file()
        assert (root / "README.md").read_text() == "# Team A"
    assert not root.exists()


def test_s3_manifest_hash_changes_only_when_object_manifest_changes() -> None:
    client = FakeS3()
    store = S3ContextStore("test-bucket", client=client)
    first = store.manifest_hash("team-a")
    assert first == store.manifest_hash("team-a")
    client.objects["sources/team-a/README.md"] = b"# Team A changed"
    assert store.manifest_hash("team-a") != first


def test_context_id_rejects_path_traversal() -> None:
    with pytest.raises(ValueError):
        validate_context_id("../secrets")


def test_dynamo_cache_round_trip() -> None:
    table = FakeTable()
    cache = DynamoContextSliceCache("unused", table=table)
    task = TaskRequest(task_type="iac_security", path="prod/main.tf", prompt="review")
    context_slice = ContextSlice(
        id="slice-1",
        scope="prod/main.tf",
        slice_type="file",
        facts=["fact"],
        sensitivity="high",
        refs=["prod/main.tf"],
        version="1",
        token_estimate=1,
    )
    assert cache.get(task) is None
    cache.put(task, [context_slice])
    hit = cache.get(task)
    assert hit is not None
    assert hit.slice_ids == ["slice-1"]
    assert hit.hits == 1


def test_compiled_slice_store_is_namespaced_by_context_and_manifest() -> None:
    table = FakeSliceTable()
    store = DynamoSliceStore("unused", table=table)
    first = ContextSlice(
        id="same-logical-id",
        scope="prod/main.tf",
        slice_type="file",
        facts=["team a"],
        sensitivity="high",
        refs=["prod/main.tf"],
        version="1",
        token_estimate=2,
    )
    second = ContextSlice(
        id="same-logical-id",
        scope="prod/main.tf",
        slice_type="file",
        facts=["team b"],
        sensitivity="high",
        refs=["prod/main.tf"],
        version="1",
        token_estimate=2,
    )
    store.put_many([first], context_id="team-a", manifest_hash="hash-a")
    store.put_many([second], context_id="team-b", manifest_hash="hash-b")

    assert store.get_many("team-a", "hash-a")[0].facts == ["team a"]
    assert store.get_many("team-b", "hash-b")[0].facts == ["team b"]
