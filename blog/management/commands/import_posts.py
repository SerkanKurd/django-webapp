import json
from django.core.management.base import BaseCommand
from blog.models import Posts
from django.conf import settings
import os
from datetime import datetime


class Command(BaseCommand):
    help = "Import posts from a JSON file"

    def handle(self, *args, **kwargs):
        json_file_path = os.path.join(
            settings.BASE_DIR,
            "static/posts.json"
        )
        print(json_file_path)

        try:
            with open(json_file_path, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(
                f"JSON file not found at {json_file_path}"))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(
                "Error decoding JSON. Please check the file format."))
            return

        posts_created_count = 0
        posts_updated_count = 0
        for post_data in data["posts"]:
            time_str = post_data.get("time")
            if time_str:
                try:
                    post_data["time"] = datetime.fromisoformat(
                        time_str.replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    self.stdout.write(self.style.WARNING(
                        f"Could not parse time '{time_str}' for post ID {post_data.get('id')}. Setting to null."))
                    post_data["time"] = None
            else:
                post_data["time"] = None

            _, created = Posts.objects.update_or_create(
                id=post_data["id"],
                defaults=post_data,
            )
            if created:
                posts_created_count += 1
            else:
                posts_updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully imported posts. Created: {posts_created_count}, Updated: {posts_updated_count}."))
