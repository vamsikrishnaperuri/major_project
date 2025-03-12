<?php
defined('MOODLE_INTERNAL') || die();

function gradereport_userperformance_extend_navigation($navigation, $context) {
    if (has_capability('gradereport/userperformance:view', $context)) {
        $url = new moodle_url('/grade/report/userperformance/index.php');
        $navigation->add(get_string('viewreport', 'gradereport_userperformance'), $url);
    }
}
