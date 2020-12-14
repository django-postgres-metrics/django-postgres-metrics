# Copyright (C) 2020 Markus Holtermann
# Copyright (C) 2020 Crate.IO GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# This code was derived from
# https://github.com/crate/crate-operator/blob/df1c8dfdf1b40d9f4bdde2d6facaa51fb483d69e/docs/source/crate_operator_ext.py

import pathlib


def run_apidoc(_):
    from sphinx.ext import apidoc

    argv = [
        "--ext-autodoc",
        "--ext-intersphinx",
        "--separate",
        "--implicit-namespaces",
        "--no-toc",
        "-o",
        str(pathlib.Path(__file__).parent / "ref"),
        str(pathlib.Path(__file__).parent.parent.parent / "postgres_metrics"),
    ]
    apidoc.main(argv)


def resolv_ref(app, env, node, contnode):
    reftarget = node.get("reftarget", "")
    if node.get("refdomain") == "py":
        if reftarget == "django.apps.config.AppConfig":
            node.attributes["reftarget"] = "django:django.apps.AppConfig"
        if reftarget == "django.db.models.base.Model":
            node.attributes["reftarget"] = "django:django.db.models.Model"


def setup(app):
    app.connect("builder-inited", run_apidoc)
    app.connect("missing-reference", resolv_ref)
