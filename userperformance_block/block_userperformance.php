<?php
class block_userperformance extends block_base {

    function init() {
        $this->title = get_string('pluginname', 'block_userperformance');
    }

    function get_content() {
        global $DB, $USER, $COURSE;

        if ($this->content !== null) {
            return $this->content;
        }

        $this->content = new stdClass;
        
        // Check if user is logged in & inside a course
        if (isloggedin() && !isguestuser() && $COURSE->id != SITEID) {

            // Query performance data
            $performance = $DB->get_record('gradereport_userperformance_data', 
                array('userid' => $USER->id, 'courseid' => $COURSE->id));
            
            if ($performance) {
                $this->content->text = '<strong>Your Performance:</strong><br>' . $performance->performance;
            } else {
                $this->content->text = 'Performance data not available.';
            }

        } else {
            $this->content->text = 'Please view inside a course.';
        }

        return $this->content;
    }
}
?>
