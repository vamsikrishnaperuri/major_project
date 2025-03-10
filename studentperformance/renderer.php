<?php
namespace local_studentperformance;

defined('MOODLE_INTERNAL') || die();

class renderer {
    private $data_file_path;

    public function __construct() {
        $this->data_file_path = __DIR__ . '/../data/performance_data.json';
    }

    /**
     * Render performance data
     */
    public function render_performance_data($courseid) {
        if (!file_exists($this->data_file_path)) {
            return 'Performance data not available.';
        }

        $data = json_decode(file_get_contents($this->data_file_path), true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            return 'Error reading performance data.';
        }

        $output = '<table>';
        $output .= '<tr><th>User ID</th><th>Course ID</th><th>Performance</th></tr>';

        foreach ($data as $entry) {
            if ($entry['course_id'] == $courseid) {
                $output .= '<tr>';
                $output .= '<td>' . htmlspecialchars($entry['user_id']) . '</td>';
                $output .= '<td>' . htmlspecialchars($entry['course_id']) . '</td>';
                $output .= '<td>' . htmlspecialchars($entry['Performance']) . '</td>';
                $output .= '</tr>';
            }
        }

        $output .= '</table>';
        return $output;
    }
}