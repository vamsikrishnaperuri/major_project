<?php

defined('MOODLE_INTERNAL') || die();

class gradereport_userperformance_renderer extends plugin_renderer_base {
    public function render_performance_table($data) {
        global $OUTPUT;

        echo "Renderer is loaded"; // Debug message

        $table = new html_table();
        $table->head = ['User ID', 'Performance'];

        foreach ($data as $row) {
            $table->data[] = [$row->userid, ucfirst($row->performance)];
        }

        return $OUTPUT->box_start() . html_writer::table($table) . $OUTPUT->box_end();
    }
}
