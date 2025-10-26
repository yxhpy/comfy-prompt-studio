"""
Web (HTML) routes.
"""
from flask import Blueprint, render_template

bp = Blueprint("web", __name__)


@bp.route("/")
def index():
    return render_template("index.html")
