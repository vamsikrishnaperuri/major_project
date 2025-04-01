<?php
defined('MOODLE_INTERNAL') || die();

class block_chatbot extends block_base {

    function init() {
        $this->title = get_string('pluginname', 'block_chatbot');
    }

    function get_content() {
        global $CFG, $USER;

        if ($this->content !== null) {
            return $this->content;
        }

        $this->content = new stdClass();
        $this->content->text = '
        <div id="chatbot-window" style="border:1px solid #ccc; padding:10px;">
            <div id="chatlog" style="height:200px; overflow-y:scroll;"></div>
            <input type="text" id="chatinput" placeholder="Ask me..." />
            <button onclick="sendChat()">Send</button>
        </div>
        <script>
            function sendChat() {
                var input = document.getElementById("chatinput").value;
                var xhr = new XMLHttpRequest();
                xhr.open("POST", "'.$CFG->wwwroot.'/blocks/chatbot/handle.php", true);
                xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
                xhr.onload = function() {
                    document.getElementById("chatlog").innerHTML += "<br><b>You:</b> " + input;
                    document.getElementById("chatlog").innerHTML += "<br><b>Bot:</b> " + xhr.responseText;
                    document.getElementById("chatinput").value = "";
                };
                xhr.send("query=" + encodeURIComponent(input));
            }
        </script>';
        return $this->content;
    }
}
