<?php
namespace local_studentperformance;

defined('MOODLE_INTERNAL') || die();

class block_studentperformance extends \block_base {
    public function init() {
        $this->title = get_string('pluginname', 'local_studentperformance');
    }

    public function get_content() {
        if ($this->content !== null) {
            return $this->content;
        }

        $this->content = new \stdClass();
        $renderer = new renderer();
        $this->content->text = $renderer->render_performance_data($this->page->course->id);

        return $this->content;
    }
}