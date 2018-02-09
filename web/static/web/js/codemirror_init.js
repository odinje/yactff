(function(){
  try {
    var type = document.getElementById('id_type').value;
  }
  catch(er) { // Hack since only pages have types
    var type = "markdown";
  }
  if (type.value == 'html') {
    var codemirror_mode = 'htmlmixed';
  } else {
    var codemirror_mode = 'markdown';
  }

    $(document).ready(function(){
        $('textarea.html-editor').each(function(idx, el){
            CodeMirror.fromTextArea(el, {
                lineNumbers: true,
                lineWrapping: false,
                autoRefresh:true,
                mode: codemirror_mode
            });
        });
    });
})();
