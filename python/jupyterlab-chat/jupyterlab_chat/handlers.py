import json

import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
from pytwd_ai.config.config_loader import PACKAGE_CONFIG


class ConfigHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        """Return configuration values from environment variables"""

        config = {
            "feedbackUrl": PACKAGE_CONFIG.power_automate_flows.pyca_feedback_logging.get_url()
        }
        self.finish(json.dumps(config))


def setup_handlers(web_app):
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]
    
    handlers = [
        (url_path_join(base_url, "jupyterlab-chat", "config"), ConfigHandler)
    ]
    
    web_app.add_handlers(host_pattern, handlers)
