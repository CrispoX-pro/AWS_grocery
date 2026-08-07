import logging
import shutil
import tempfile
import zipfile
import os
import socket
import requests

import boto3
import watchtower

from logging.handlers import RotatingFileHandler
from flask import Flask, send_from_directory, render_template, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from sqlalchemy import text
from flask_migrate import Migrate
from dotenv import load_dotenv
from datetime import timedelta
from dateutil import parser


load_dotenv()

db = SQLAlchemy()


DEPLOYMENT_ENV = os.getenv("DEPLOYMENT_ENV", "local")

GITHUB_USERNAME = "AlejandroRomanIbanez"
REPO_NAME = "AWS_grocery"

FRONTEND_BUILD_ZIP = "frontend-build.zip"

FRONTEND_BUILD_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../frontend/build")
)

TMP_ZIP_PATH = os.path.join(
    tempfile.gettempdir(),
    "frontend-build.zip"
)

GITHUB_RELEASE_URL = (
    f"https://github.com/{GITHUB_USERNAME}/{REPO_NAME}"
    f"/releases/latest/download/{FRONTEND_BUILD_ZIP}"
)


class Config:
    """
    App configuration variables.
    """

    POSTGRES_URI = os.getenv(
        "POSTGRES_URI",
        "postgresql://postgres:postgres@localhost:5432/postgres"
    )

    if not POSTGRES_URI:
        raise ValueError(
            "POSTGRES_URI environment variable is not set."
        )

    @classmethod
    def is_rds(cls):
        """
        Detect AWS RDS database.
        """
        return (
            "rds.amazonaws.com" in cls.POSTGRES_URI
            or "amazonaws.com" in cls.POSTGRES_URI
        )

    @classmethod
    def is_local_postgres(cls):
        return not cls.is_rds()


    SQLALCHEMY_DATABASE_URI = POSTGRES_URI

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "change-me"
    )

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=4)


print(
    f"Using Database: {Config.SQLALCHEMY_DATABASE_URI}"
)


def detect_environment():

    if Config.is_rds():
        print("Running on AWS RDS (Production)")

    elif Config.is_local_postgres():
        print("Running in Local PostgreSQL")

    else:
        print(
            "Could not detect database environment"
        )

    print(
        f"Using Database: {Config.SQLALCHEMY_DATABASE_URI}"
    )


detect_environment()



def fetch_frontend():
    """
    Download frontend build from GitHub Release.
    """

    if os.path.exists(FRONTEND_BUILD_PATH):

        print(
            "Frontend build exists. Checking updates..."
        )

        latest_release_timestamp = (
            get_github_release_timestamp()
        )

        local_build_timestamp = (
            get_local_build_timestamp()
        )

        if (
            latest_release_timestamp
            and local_build_timestamp
            and local_build_timestamp >= latest_release_timestamp
        ):
            print(
                "Frontend build is up to date."
            )
            return

    else:
        print(
            "Frontend build missing. Downloading..."
        )


    try:

        response = requests.get(
            GITHUB_RELEASE_URL,
            stream=True
        )


        if response.status_code != 200:
            print(
                f"Frontend download failed: {response.status_code}"
            )
            return


        with open(TMP_ZIP_PATH, "wb") as file:
            file.write(response.content)


        frontend_dir = os.path.dirname(
            FRONTEND_BUILD_PATH
        )

        os.makedirs(
            frontend_dir,
            exist_ok=True
        )


        temp_extract_path = os.path.join(
            frontend_dir,
            "temp_extract"
        )


        shutil.rmtree(
            temp_extract_path,
            ignore_errors=True
        )


        os.makedirs(
            temp_extract_path
        )


        with zipfile.ZipFile(
            TMP_ZIP_PATH,
            "r"
        ) as zip_ref:

            zip_ref.extractall(
                temp_extract_path
            )


        if os.path.exists(FRONTEND_BUILD_PATH):

            shutil.rmtree(
                FRONTEND_BUILD_PATH
            )


        os.makedirs(
            FRONTEND_BUILD_PATH
        )


        if os.path.exists(
            os.path.join(
                temp_extract_path,
                "build",
                "index.html"
            )
        ):

            source_dir = os.path.join(
                temp_extract_path,
                "build"
            )

        elif os.path.exists(
            os.path.join(
                temp_extract_path,
                "index.html"
            )
        ):

            source_dir = temp_extract_path

        else:

            raise Exception(
                "index.html not found"
            )


        for item in os.listdir(source_dir):

            source = os.path.join(
                source_dir,
                item
            )

            destination = os.path.join(
                FRONTEND_BUILD_PATH,
                item
            )


            if os.path.isdir(source):

                shutil.copytree(
                    source,
                    destination
                )

            else:

                shutil.copy2(
                    source,
                    destination
                )


        print(
            "Frontend successfully updated"
        )


        shutil.rmtree(
            temp_extract_path,
            ignore_errors=True
        )


        os.remove(
            TMP_ZIP_PATH
        )


    except Exception as e:

        print(
            f"Frontend error: {e}"
        )

        raise
def get_github_release_timestamp():
    """
    Gets latest frontend release timestamp.
    """

    release_api_url = (
        f"https://api.github.com/repos/"
        f"{GITHUB_USERNAME}/{REPO_NAME}/releases/latest"
    )

    try:

        response = requests.get(
            release_api_url
        )


        if response.status_code == 200:

            timestamp_iso = (
                response.json()
                .get("published_at")
            )

            if timestamp_iso:

                return int(
                    parser.parse(timestamp_iso)
                    .timestamp()
                )


    except Exception as e:

        print(
            f"GitHub timestamp error: {e}"
        )


    return None



def get_local_build_timestamp():

    try:

        return os.path.getmtime(
            FRONTEND_BUILD_PATH
        )

    except Exception:

        return None



def create_app():
    """
    Creates and configures Flask application.
    """

    fetch_frontend()


    app = Flask(
        __name__,
        static_folder="../../frontend/build/static",
        template_folder=os.path.join(
            os.path.dirname(__file__),
            "../../frontend/build"
        )
    )


    CORS(
        app,
        resources={
            r"/*": {
                "origins": "*"
            }
        }
    )


    app.config.from_object(
        Config
    )


    db.init_app(
        app
    )


    with app.app_context():

        if app.config[
            "SQLALCHEMY_DATABASE_URI"
        ].startswith("sqlite"):

            db.session.execute(
                text(
                    "PRAGMA foreign_keys=ON"
                )
            )


    JWTManager(
        app
    )


    Migrate(
        app,
        db
    )


    setup_logging(
        app
    )


    from .routes.auth_routes import auth_bp
    from .routes.user_routes import user_bp
    from .routes.product_routes import product_bp
    from .routes.health_routes import health_bp
    from .routes.config_routes import config_bp


    app.register_blueprint(
        auth_bp
    )

    app.register_blueprint(
        user_bp
    )

    app.register_blueprint(
        product_bp
    )

    app.register_blueprint(
        health_bp
    )

    app.register_blueprint(
        config_bp
    )



    def inject_backend_url():

        proto = request.headers.get(
            "X-Forwarded-Proto",
            request.scheme
        )

        host = request.headers.get(
            "X-Forwarded-Host",
            request.host
        )


        return (
            f"{proto}://{host}"
        )



    @app.route(
        "/",
        defaults={
            "path": ""
        }
    )

    @app.route(
        "/<path:path>"
    )

    def serve_react_app(path):

        if (
            path
            and os.path.exists(
                os.path.join(
                    app.static_folder,
                    path
                )
            )
        ):

            return send_from_directory(
                app.static_folder,
                path
            )


        return render_template(
            "index.html",
            backend_url=inject_backend_url()
        )


    return app

def setup_logging(app):
    """
    Logging:
    - lokale Datei logs/app.log
    - AWS CloudWatch Logs
    """


    if not os.path.exists(
        "logs"
    ):

        os.mkdir(
            "logs"
        )


    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


    #
    # Lokales Logging
    #

    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=1024 * 1024,
        backupCount=5
    )


    file_handler.setLevel(
        logging.INFO
    )


    file_handler.setFormatter(
        formatter
    )


    app.logger.addHandler(
        file_handler
    )



    #
    # CloudWatch Logging
    #

    cloudwatch_enabled = (
        os.getenv(
            "ENABLE_CLOUDWATCH",
            "false"
        )
        .lower()
        == "true"
    )


    if cloudwatch_enabled:


        log_group = os.getenv(
            "CLOUDWATCH_LOG_GROUP",
            "/aws/ec2/grocerymate"
        )


        log_stream = os.getenv(
            "CLOUDWATCH_LOG_STREAM",
            socket.gethostname()
        )


        try:

            cloudwatch_handler = watchtower.CloudWatchLogHandler(
                log_group=log_group,
                stream_name=log_stream,
                boto3_client=boto3.client(
                    "logs",
                    region_name=os.getenv(
                        "AWS_REGION",
                        "eu-central-1"
                    )
                )
            )


            cloudwatch_handler.setLevel(
                logging.INFO
            )


            cloudwatch_handler.setFormatter(
                formatter
            )


            app.logger.addHandler(
                cloudwatch_handler
            )


            app.logger.info(
                "CloudWatch logging enabled"
            )


        except Exception as e:

            app.logger.error(
                f"CloudWatch setup failed: {e}"
            )


    app.logger.setLevel(
        logging.INFO
    )


    app.logger.info(
        "Application logging initialized"
    )