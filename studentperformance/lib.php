<?php
defined('MOODLE_INTERNAL') || die();

function local_studentperformance_extend_course_navigation($coursemodinfo) {
    global $PAGE, $OUTPUT;

    if ($coursemodinfo->get_course()->id > 1) {
        $performance_manager = new \local_studentperformance\performance_manager();
        $performance_data = $performance_manager->get_course_performance_data($coursemodinfo->get_course()->id);

        if (!empty($performance_data)) {
            $template_data = [
                'has_data' => true,
                'performances' => $performance_data
            ];

            $performance_html = $OUTPUT->render_from_template('local_studentperformance/performance_display', $template_data);
            $PAGE->requires->js_call_amd('local_studentperformance/display', 'init', [$performance_html]);
        }
    }
}