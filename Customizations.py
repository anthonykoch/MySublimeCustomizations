import sublime_plugin, sublime, sys, os
from sublime import Region
from functools import partial

from Customizations.Settings import Settings
from Customizations.Utils import ignore, all_views
from collections import defaultdict




# User settings from User/Customizations.sublime-settings
user_settings = None




# Set the file size in the status bar 
def set_file_size(view):
	# Getting the number of bytes seems to be more accurate than sys.getsizeof
	file_size = len(view.substr(Region(0, view.size())).encode('utf-8'))
	view.set_status(
			'file_size',
			'{0:.2F} KB'.format(file_size / 1000)
		)

# If the file is unsaved, display "Unsaved" in the status bar, else display nothing
def set_file_saved(view):
	view.set_status(
			'file_saved',
			'Unsaved' if view.is_dirty() else ''
		)




view_sizes = defaultdict(int)

class StatusBarListener(sublime_plugin.EventListener):

	def on_activated_async(self, view):
		view_id = view.id()
		view_size = view.size()
		view_sizes[view_id] = view_size
		
		set_file_size(view)
		set_file_saved(view)

	def on_modified_async(self, view):
		view_id = view.id()
		view_size = view.size()
		
		# Only update the file size status if more than n characters have been added or deleted 
		if abs(view_sizes[view_id] - view_size) > user_settings.get('character_count'):
			view_sizes[view_id] = view_size
			set_file_size(view)

		set_file_saved(view)
		
	def on_post_save_async(self, view):
		set_file_saved(view)

	def on_load_async(self, view):
		set_file_size(view)

		# Set vagrant files to Ruby syntax 
		basename = os.path.basename(view.file_name())
		if basename == 'Vagrantfile':
			view.set_syntax_file('Packages/Ruby/Ruby.tmLanguage')



class SideBarListener(sublime_plugin.EventListener):

	def on_window_command(self, window, command_name, args):
		# Close a file when it is deleted from the sidebar 
		if command_name == 'side_bar_delete':
			
			files = args['paths']
			
			for view in all_views():
				if view.file_name() in files:
					view.set_scratch(True)
					window.focus_view(view)
					window.run_command('close_file')










IS_FAILURE = 0
IS_SUCCESS = 1

ACTION_UPDATE = 2
ACTION_REMOVE = 4
ACTION_RESET = 8

ON_STATUS_BAR = 1




def handle_received(data):

	print(data)
	
	with ignore(Exception, message="handle_received"):

		action = data['action']
		perform_on = data['perform_on']
		view_ids = data.get('view_ids')
		
		active_view = sublime.active_window().active_view()

		if action & ACTION_UPDATE:
			if perform_on & ON_STATUS_BAR:
				[view.set_status(
						data['status_id'], 
						data.get('status', '')
					) for view in all_views()]

		elif action & ACTION_REMOVE:
			pass

		elif action & ACTION_RESET:
			if perform_on & ON_STATUS_BAR:
				[view.set_status(
						data['status_id'], 
						''
					) for view in all_views()]





def plugin_loaded():
	global user_settings
	user_settings = Settings()
	user_settings.load()

	# Set the file size in the active view 
	view = sublime.active_window().active_view()
	set_file_size(view)
	set_file_saved(view)
	

	from Customizations.Server import on_received
	on_received(handle_received)



