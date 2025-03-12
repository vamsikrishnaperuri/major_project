<?php
require('../../config.php');
require_once($CFG->dirroot.'/grade/lib.php');
require_once($CFG->dirroot.'/grade/report/userperformance/locallib.php');
require_once($CFG->dirroot . '/grade/report/userperformance/renderer.php');
require_once($CFG->dirroot.'/grade/report/userperformance/lib.php');


$courseid = required_param('id', PARAM_INT);
$course = $DB->get_record('course', ['id' => $courseid], '*', MUST_EXIST);
require_login($course);

$context = context_course::instance($courseid);
require_capability('gradereport/userperformance:view', $context);

$PAGE->set_url('/grade/report/userperformance/index.php', ['id' => $courseid]);
$PAGE->set_context($context);
$PAGE->set_title('User Performance Report');
$PAGE->set_heading('User Performance Report');

echo $OUTPUT->header();
echo '<h2>User Performance Report</h2>';
$table = new html_table();
$table->head = ['User ID', 'Performance'];

$users = get_enrolled_users($context);
foreach ($users as $user) {
    $data = gradereport_userperformance_get_data($user->id, $courseid);
    $performance = $data ? $data->performance : 'Not Available';
    $table->data[] = [$user->id, $performance];
}

echo html_writer::table($table);
echo $OUTPUT->footer();
