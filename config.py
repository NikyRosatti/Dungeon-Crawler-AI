"""
Configuration file for the Flask application.

This module defines different configuration classes for the application, 
including the base configuration,development, testing, and production environments. 
It also loads environment variables from a .env file.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Base configuration class.

    This class contains the general configuration settings that are common across 
    different environments.
    It includes settings for the database, language, and other configuration options.
    """

    base_dir = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    if os.getenv('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///dataBase.db'

    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_SUPPORTED_LOCALES = ['en', 'es']
    BABEL_TRANSLATION_DIRECTORIES = os.path.join(base_dir, "translations")


class DevelopmentConfig(Config):
    """
    Configuration for the development environment.

    This class inherits from the base configuration class and adds or overrides 
    settings specific to the development environment, such as enabling debug mode 
    and setting the development database URI.
    """

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DEV_DATABASE_URL', 'sqlite:///dev_database.db')


class TestConfig(Config):
    """
    Configuration for the testing environment.

    This class inherits from the base configuration class and adds or overrides 
    settings specific to the testing environment, such as enabling testing mode,
    debug mode, and disabling CSRF protection.
    """

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL', 'sqlite:///test.db')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """
    Configuration for the production environment.

    This class inherits from the base configuration class and provides the 
    settings for the production environment, including the production database URI.
    """

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
