<?php
class block_course_performance_feedback extends block_base {

    function init() {
        $this->title = get_string('pluginname', 'block_course_performance_feedback');
    }

    function get_content() {
        global $DB, $USER, $COURSE;

        if ($this->content !== null) {
            return $this->content;
        }

        $this->content = new stdClass;
        
        if (isloggedin() && !isguestuser()) {
            $context = context_course::instance($COURSE->id);
            $is_teacher = has_capability('block/course_performance_feedback:viewall', $context);
            
            if ($COURSE->id != SITEID) {
                if ($is_teacher) {
                    // Teacher: View all students performance
                    $records = $DB->get_records('gradereport_userperformance_data', ['courseid' => $COURSE->id]);
                    
                    if ($records) {
                        $output = '<strong>Students Performance in this Course:</strong><br>';
                        foreach ($records as $record) {
                            $student = $DB->get_record('user', ['id' => $record->userid]);
                            $output .= fullname($student) . ': ' . $record->performance . '<br>';
                        }
                        $this->content->text = $output;
                    } else {
                        $this->content->text = 'No performance data available for students.';
                    }

                } else {
                    // Student: View own performance
                    $records = $DB->get_records('gradereport_userperformance_data', ['userid' => $USER->id]);
                    
                    if ($records) {
                        $poor_courses = [];
                        $good_courses = [];
                        foreach ($records as $record) {
                            $course = $DB->get_record('course', ['id' => $record->courseid]);
                            if (strpos(strtolower($record->performance), 'poor') !== false) {
                                $poor_courses[] = $course->fullname;
                            } else {
                                $good_courses[] = $course->fullname;
                            }
                        }

                        $output = '<strong>Your Performance Summary:</strong><br>';
                        if (!empty($poor_courses)) {
                            $output .= 'You need to improve in: ' . implode(', ', $poor_courses) . '<br>';
                        }
                        if (!empty($good_courses)) {
                            $output .= 'You are performing well in: ' . implode(', ', $good_courses) . '<br>';
                        }
                        $this->content->text = $output;
                    } else {
                        $this->content->text = 'No performance data available.';
                    }
                }

            } else {
                $this->content->text = 'Please view inside a course.';
            }
        } else {
            $this->content->text = 'Please log in to view performance data.';
        }

        return $this->content;
    }
}
?>
