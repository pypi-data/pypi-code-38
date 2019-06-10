# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Widgets classes used by platforms supporting non-interactive HTML widgets."""
import datetime
import jinja2
import base64
import uuid


def _walk_and_update_time_object(d):
    if isinstance(d, dict):
        for k, v in d.items():
            _walk_and_update_time_object(v)
            if isinstance(v, datetime.datetime):
                d[k] = v.isoformat()
    elif isinstance(d, list):
        for x in d:
            _walk_and_update_time_object(x)


class _RunWidgetBase:
    """Base class for run widget."""

    runType = ''
    widget_settings = ''
    selected_run_id = ''
    run_properties = ''
    run_logs = ''
    run_metrics = ''
    run_id = ''
    run_arguments = ''
    child_runs = ''
    child_runs_metrics = ''
    workbench_uri = ''
    graph = ''

    frame = """<!DOCTYPE html>
            <meta charset="utf-8">
            <head>
              <link rel="stylesheet" type="text/css"
                    href="https://amlwidgetcdn.blob.core.windows.net/amlwidgetcdn/style/notebook-5.3.1.style.min.css">
            </head>
            <body>
            <div>Widgets on this platform are experimental and subject to future change or removal.</div>
            <div id='{{GUID}}'></div>
            <script src="https://amlwidgetcdn.blob.core.windows.net/amlwidgetcdn/script/require-2.3.5.js"></script>
            <script src="https://amlwidgetcdn.blob.core.windows.net/amlwidgetcdn/script/jquery-3.3.1.min.js"></script>
            <script>
                var cdnPath = "https://amlwidgetcdn.blob.core.windows.net/amlwidgetcdn/azureml-widgets/1.0/";
                if (window.require) {
                    window.require.config({
                        map: {
                            "*" : {
                                "azureml_contrib_widgets": cdnPath + "index.js",
                            }
                        }
                    });
                }
                require(["azureml_contrib_widgets"], function(widgets){
                    // backfill python preserved words
                    var False = false;
                    var True = true;
                    var None = null;
                    var id = '{{GUID}}';
                    runType = '{{runType}}';
                    value = {{value}};

                    value.run_logs = atob(value.run_logs);
                    if(runType==='HyperDrive'){
                        widgets.ShowHyperDriveRunsView.prototype.render(value, $('#'+id));
                    }
                    else if (runType==='AutoML'){
                        widgets.ShowAutoMLRunsView.prototype.render(value, $('#'+id));
                    }
                    else{
                        widgets.ShowRunDetailsView.prototype.render(value, $('#'+id));
                    }
                })
            </script>"""

    def get_html(self):
        """Return HTML string representation of the widget to be rendered by the platform."""
        value = {
            "widget_settings": self.widget_settings,
            "selected_run_id": self.selected_run_id,
            "run_properties": self.run_properties,
            # decode in the end is to remove b''
            "run_logs": base64.b64encode(bytearray(self.run_logs.encode())).decode(),
            "run_metrics": self.run_metrics,
            "run_id": self.run_id,
            "run_arguments": self.run_arguments,
            "child_runs": self.child_runs,
            "child_runs_metrics": self.child_runs_metrics,
            "workbench_uri": self.workbench_uri,
            'graph': self.graph
        }
        # can't serialize datetime object so modify them to ISO string
        _walk_and_update_time_object(value)
        template = jinja2.Template(self.frame)
        return template.render(runType=self.runType, value=value, GUID=uuid.uuid4())
