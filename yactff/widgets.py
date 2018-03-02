from django import forms


class CodeMirrorWidget(forms.Textarea):
    def __init__(self, *args, **kwargs):
        super(CodeMirrorWidget, self).__init__(*args, **kwargs)
        self.attrs['class'] = 'html-editor'

    class Media:
        css = {
            'all': (
                '/static/codemirror/css/codemirror.css',
            )
        }
        js = (
            '/static/codemirror/js/codemirror.js',
            '/static/codemirror/js/autorefresh.js',
            '/static/codemirror/js/mode/xml.js',
            '/static/codemirror/js/mode/markdown.js',
            '/static/codemirror/js/mode/htmlmixed.js',
            '/static/web/js/codemirror_init.js'
            )
