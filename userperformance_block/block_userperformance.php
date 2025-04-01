<?php
class block_userperformance extends block_base {

    function init() {
        $this->title = get_string('pluginname', 'block_userperformance');
    }

    function applicable_formats() {
        return [
            'site-index' => true,
            'course-view' => true,
            'my' => true,
        ];
    }

    function get_content() {
        global $DB, $USER;

        $this->content = new stdClass;

        $is_teacher = has_capability('moodle/course:update', context_system::instance(), $USER);

        if ($is_teacher) {
            $this->content->text = '<h4>Student Performance</h4>';

            $students = $DB->get_records_sql("
                SELECT u.id, u.firstname, u.lastname
                FROM {user} u
                INNER JOIN {role_assignments} ra ON ra.userid = u.id
                INNER JOIN {role} r ON r.id = ra.roleid
                WHERE r.shortname = 'student'
            ");

            foreach ($students as $student) {
                $this->content->text .= '<h5>' . fullname($student) . '</h5>';

                $performances = $DB->get_records('gradereport_userperformance_data', ['userid' => $student->id]);

                if ($performances) {
                    foreach ($performances as $p) {
                        $course = $DB->get_record('course', ['id' => $p->courseid]);
                        if ($p->performance == 'Poor Performance') {
                            $this->content->text .= '<strong>' . format_string($course->fullname) . ':</strong> ';
                            $this->content->text .= '<span style="color:red;">Needs Improvement</span><br>';

                            // Fetch weak topics
                            $weak_topics = $this->get_weak_topics($student->id, $course->id);

                            if (!empty($weak_topics)) {
                                $this->content->text .= '<strong>Topics/Assignments to Improve:</strong> ';
                                $this->content->text .= implode(', ', $weak_topics) . '<br>';
                            }
                        } else {
                            $this->content->text .= '<strong>' . format_string($course->fullname) . ':</strong> ' . $p->performance . '<br>';
                        }
                    }
                } else {
                    $this->content->text .= 'No performance data available.<br>';
                }
                $this->content->text .= '<hr>';
            }
        } else { // STUDENT VIEW
            $performances = $DB->get_records('gradereport_userperformance_data', ['userid' => $USER->id]);

            if ($performances) {
                $text = '<h4>Your Course Performance</h4>';
                foreach ($performances as $p) {
                    $course = $DB->get_record('course', ['id' => $p->courseid]);
                    if ($p->performance == 'Poor Performance') {
                        $text .= '<strong>' . format_string($course->fullname) . ':</strong> ';
                        $text .= '<span style="color:red;">Needs Improvement</span><br>';

                        $weak_topics = $this->get_weak_topics($USER->id, $course->id);

                        if (!empty($weak_topics)) {
                            $text .= '<strong>Topics/Assignments to Improve:</strong> ';
                            $text .= implode(', ', $weak_topics) . '<br>';
                        }
                    } else {
                        $text .= '<strong>' . format_string($course->fullname) . ':</strong> ' . $p->performance . '<br>';
                    }
                }
                $this->content->text = $text;
            } else {
                $this->content->text = 'No performance data available.';
            }
        }

        return $this->content;
    }

    // Updated weak topic function to include both quizzes & assignments
    private function get_weak_topics($userid, $courseid) {
        global $DB;
    
        $threshold = 50; // Grade threshold %
    
        $weak_topics = [];
    
        // Check for Quizzes
        $quizzes = $DB->get_records('quiz', ['course' => $courseid]);
        foreach ($quizzes as $quiz) {
            $grade_item = $DB->get_record('grade_items', [
                'iteminstance' => $quiz->id,
                'itemmodule' => 'quiz',
                'courseid' => $courseid
            ]);
    
            if ($grade_item) {
                $grade = $DB->get_record('grade_grades', [
                    'userid' => $userid,
                    'itemid' => $grade_item->id
                ]);
    
                if ($grade && !is_null($grade->finalgrade)) {
                    $maxgrade = $grade_item->grademax;
                    $percentage = ($grade->finalgrade / $maxgrade) * 100;
    
                    if ($percentage < $threshold) {
                        $description = !empty($quiz->intro) ? strip_tags($quiz->intro) : 'Quiz';
                        $weak_topics[] = 'Quiz: ' . $description;
                    }
                }
            }
        }
    
        // Check for Assignments
        $assignments = $DB->get_records('assign', ['course' => $courseid]);
        foreach ($assignments as $assignment) {
            $grade_item = $DB->get_record('grade_items', [
                'iteminstance' => $assignment->id,
                'itemmodule' => 'assign',
                'courseid' => $courseid
            ]);
    
            if ($grade_item) {
                $grade = $DB->get_record('grade_grades', [
                    'userid' => $userid,
                    'itemid' => $grade_item->id
                ]);
    
                if ($grade && !is_null($grade->finalgrade)) {
                    $maxgrade = $grade_item->grademax;
                    $percentage = ($grade->finalgrade / $maxgrade) * 100;
    
                    if ($percentage < $threshold) {
                        $description = !empty($assignment->intro) ? strip_tags($assignment->intro) : 'Assignment';
                        $weak_topics[] = 'Assignment: ' . $description;
                    }
                }
            }
        }
    
        return $weak_topics;
    }
}
?>
