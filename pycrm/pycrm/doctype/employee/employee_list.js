frappe.listview_settings['Employee'] = {
	onload: function(listview) {
		listview.page.add_menu_item(__("Enable"), function() {
			show_alert('Action Unavailale', 5);
		});
	}
};
