#!/usr/bin/env python
# encoding: utf-8

"""
NPSAppManaged.py
"""

from . import apNPSApplication
import weakref


class NPSAppManaged(apNPSApplication.NPSApp):
    """This class is intended to make it easier to program applications with many screens:
    
    1. The programmer should not now select which 'Form' to display himself.  Instead, he should set the
       NEXT_ACTIVE_FORM class variable. See the registerForm method for details.
       
       Doing this will avoid accidentally exceeding the maximum recursion depth.  Forms themselves should be placed
       under the management of the class using the 'addForm' or 'addFormClass' method.
       
       NB. * Applications should therefore use this mechanism in preference to calling the .edit() method of any form. *
       
    2. Forms that are managed by this class can access a proxy to the parent application through their ".parentApp"
       attribute, which is created by this class.
       
    3. a Optionally, Forms managed by this class may be given an .activate method, which will be called instead of their
       .edit loop
       
       b If not given an .activate method, any .after_editing method which a form possesses will be called after .edit()
         has exited. 3b is the preferred method to change NEXT_ACTIVE_FORM
         
    4. The method on_in_main_loop is called after each screen has exited. This can be overridden.
    
    5. This method should be able to see which screen was last active using the self._LAST_NEXT_ACTIVE_FORM attribute,
       which is only set just before each screen is displayed.
       
    6. Unless you override the attribute STARTING_FORM, the first form to be called should be named 'MAIN'
    
    7. Do override the on_start and on_clean_exit functions if you wish.
    
    """

    STARTING_FORM = "MAIN"

    def __init__(self):
        super(NPSAppManaged, self).__init__()
        self._FORM_VISIT_LIST = []
        self.NEXT_ACTIVE_FORM = self.__class__.STARTING_FORM
        self._LAST_NEXT_ACTIVE_FORM = None
        self._Forms = {}
        self.LAST_ACTIVE_FORM_NAME = None
        self._THIS_FORM = None
        self.ACTIVE_FORM_NAME = None
    
    def add_form_class(self, form_id, form_class, *args, **keywords):
        self._Forms[form_id] = [form_class, args, keywords]
    
    def add_form(self, form_id, form_class, *args, **keywords):
        """
        Create a form of the given class. f_id should be a string which will uniquely identify the form. *args will
        be passed to the Form constructor. Forms created in this way are handled entirely by the NPSAppManaged class.
        """
        form = form_class(parent_app=self, *args, **keywords)
        self.register_form(form_id, form)
        return weakref.proxy(form)
        
    def register_form(self, form_id, form):
        """form_id should be a string which should uniquely identify the form.  fm should be a Form."""
        form.parentApp = weakref.proxy(self)
        self._Forms[form_id] = form
        
    def remove_form(self, form_id):
        del self._Forms[form_id].parentApp
        del self._Forms[form_id]
    
    def get_form(self, name):
        f = self._Forms[name]
        return weakref.proxy(f)

    def set_next_form(self, form_id):
        """
        Set the form that will be selected when the current one exits.
        """
        self.NEXT_ACTIVE_FORM = form_id

    def switch_form(self, form_id):
        """
        Immediately switch to the form specified by fmid.
        """
        self._THIS_FORM.editing = False
        self.set_next_form(form_id)
        self.switch_form_now()
        
    def switch_form_now(self):
        self._THIS_FORM.editing = False
        try:
            self._THIS_FORM._widgets__[self._THIS_FORM.editw].editing = False
        except (AttributeError, IndexError):
            pass
        # Following is necessary to stop two key presses being needed for title fields
        try:
            self._THIS_FORM._widgets__[self._THIS_FORM.editw].entry_widget.editing = False
        except (AttributeError, IndexError):
            pass

    def remove_last_form_from_history(self):
        self._FORM_VISIT_LIST.pop()
        self._FORM_VISIT_LIST.pop()
            
    def switch_form_previous(self):
        self.set_next_form_previous()
        self.switch_form_now()
        
    def set_next_form_previous(self, backup=STARTING_FORM):
        try:
            if self._THIS_FORM.FORM_NAME == self._FORM_VISIT_LIST[-1]:
                self._FORM_VISIT_LIST.pop()  # Remove the current form. if it is at the end of the list
            if self._THIS_FORM.FORM_NAME == self.NEXT_ACTIVE_FORM:
                # take no action if it looks as if someone has already set the next form.
                self.set_next_form(self._FORM_VISIT_LIST.pop())  # Switch to the previous form if one exists
        except IndexError:
            self.set_next_form(backup)
            
    def get_history(self):
        return self._FORM_VISIT_LIST

    def reset_history(self):
        self._FORM_VISIT_LIST = []

    def main(self):
        """
        This function starts the application. It is usually called indirectly through the function .run().  
        You should not override this function, but override the on_in_main_loop, on_start and
        on_clean_exit methods instead, if you need to modify the application's behaviour.

        When this method is called, it will activate the form named by the class variable STARTING_FORM.  By default
        this Form will be called
        'MAIN'.  

        When that form exits (user selecting an ok button or the like), the form named by object variable
        NEXT_ACTIVE_FORM will be activated.

        If NEXT_ACTIVE_FORM is None, the main() loop will exit.
        
        The form selected will be edited using it's .edit() method UNLESS it has been provided with an .activate()
        method, in which case that method will be called instead.  This is done so that the same class of form can be
        made NPSAppManaged aware and have the normal non-NPSAppManaged edit loop.
        
        After a Form has been edited, if it has an .after_editing method, this will be called, unless it was invoked
        with the activate() method. A similar .before_editing method will be called if it exists before editing the
        form. Again, the presence of a .activate method will override this behaviour.
        
        Note that NEXT_ACTIVE_FORM is a string that is the name of the form that was specified when .addForm or
        .registerForm was called.
        """
        
        self.on_start()
        while self.NEXT_ACTIVE_FORM != "" and self.NEXT_ACTIVE_FORM is not None:
            self._LAST_NEXT_ACTIVE_FORM = self._Forms[self.NEXT_ACTIVE_FORM]
            self.LAST_ACTIVE_FORM_NAME = self.NEXT_ACTIVE_FORM

            try:
                form_class, a, k = self._Forms[self.NEXT_ACTIVE_FORM]
                self._THIS_FORM = form_class(parent_app=self, *a, **k)
            except TypeError:    
                self._THIS_FORM = self._Forms[self.NEXT_ACTIVE_FORM]

            self._THIS_FORM.FORM_NAME = self.NEXT_ACTIVE_FORM
            self.ACTIVE_FORM_NAME = self.NEXT_ACTIVE_FORM

            if len(self._FORM_VISIT_LIST) > 0:
                if self._FORM_VISIT_LIST[-1] != self.NEXT_ACTIVE_FORM:
                    self._FORM_VISIT_LIST.append(self.NEXT_ACTIVE_FORM)
            else:
                self._FORM_VISIT_LIST.append(self.NEXT_ACTIVE_FORM)

            if hasattr(self._THIS_FORM, "activate"):
                self._THIS_FORM.resize()
                self._THIS_FORM.activate()
            else:
                if hasattr(self._THIS_FORM, "before_editing"):
                    self._THIS_FORM.before_editing()
                self._THIS_FORM.resize()
                self._THIS_FORM.edit()
                if hasattr(self._THIS_FORM, "after_editing"):
                    self._THIS_FORM.after_editing()
            
            self.on_in_main_loop()
        self.on_clean_exit()
        
    def on_in_main_loop(self):
        """
        Called between each screen while the application is running. Not called before the first screen. Override at
        will
        """
        pass
        
    def on_start(self):
        """
        Override this method to perform any initialisation.
        """
        pass
                
    def on_clean_exit(self):
        """Override this method to perform any cleanup when application is exiting without error."""
