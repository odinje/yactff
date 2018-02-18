from django import forms


class CodeMirrorWidget(forms.Textarea):
    def __init__(self, *args, **kwargs):
        super(CodeMirrorWidget, self).__init__(*args, **kwargs)
        self.attrs['class'] = 'html-editor'

    class Media:
        css = {
            'all': (
                'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.9.0/codemirror.css',
            )
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.9.0/codemirror.js',
            'https://codemirror.net/addon/display/autorefresh.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.9.0/mode/xml/xml.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.9.0/mode/markdown/markdown.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.9.0/mode/htmlmixed/htmlmixed.js',
            '/static/web/js/codemirror_init.js'
        )
      

class ReadOnlyWidget(forms.widgets.Widget):
    """Some of these values are read only - just a bit of text..."""
    def render(self, _, value, attrs=None):
        return value
