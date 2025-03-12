<?php
namespace gradereport_userperformance\output;

defined('MOODLE_INTERNAL') || die();

class report implements \renderable, \templatable {
    private $courseid;

    public function __construct($courseid) {
        $this->courseid = $courseid;
    }

    public function export_for_template(\renderer_base $output) {
        global $DB;

        $context = \context_course::instance($this->courseid);
        $users = get_enrolled_users($context);
        $reportdata = [];

        foreach ($users as $user) {
            $data = $DB->get_record('gradereport_userperformance_data', ['userid' => $user->id, 'courseid' => $this->courseid]);
            $performance = $data ? ucfirst($data->performance) : 'Not Available';
            $reportdata[] = ['userid' => $user->id, 'fullname' => fullname($user), 'performance' => $performance];
        }

        return ['courseid' => $this->courseid, 'users' => $reportdata];
    }
}
