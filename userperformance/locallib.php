<?php
defined('MOODLE_INTERNAL') || die();

function gradereport_userperformance_get_data($userid, $courseid) {
    global $DB;
    return $DB->get_record('gradereport_userperformance_data', ['userid' => $userid, 'courseid' => $courseid]);
}
