

/** @odoo-module **/
import { registry } from "@web/core/registry";
const { onMounted } = owl;
const { Component } = owl;
const { useRef } = owl;

class EnableEditingButton extends Component {
    setup() {
        this.button = useRef("enableEditBtn");
        onMounted(() => {
            const btn = this.button.el;
            btn.addEventListener("click", () => {
                // Set boolean field true directly in UI
                const field = this.props.record.data;
                field.is_editable_bool = true;
            });
        });
    }
}

EnableEditingButton.template = "crm_customizations.EnableEditingButton";
registry.category("view_widgets").add("enable_edit_button", EnableEditingButton);