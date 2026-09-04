"""CLI and Entrypoint for aws_s3_local_gateway."""
import argparse

from .storage import LocalS3Gateway


def main() -> None:
    parser = argparse.ArgumentParser(description="AWS S3 Local Sovereign Gateway")
    parser.add_argument("--bucket", type=str, default="default-bucket", help="Bucket name")
    parser.add_argument("--action", type=str, choices=["init", "list", "put", "get"], default="init")
    args = parser.parse_args()

    gateway = LocalS3Gateway()
    if args.action == "init":
        gateway.create_bucket(args.bucket)
        print(f"[LocalS3Gateway] Initialized bucket: {args.bucket}")
    elif args.action == "list":
        res = gateway.list_objects_v2(args.bucket)
        print(f"[LocalS3Gateway] {args.bucket} contains {res['KeyCount']} objects.")


if __name__ == "__main__":
    main()
