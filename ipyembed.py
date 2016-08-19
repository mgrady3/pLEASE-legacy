"""
Simple hack to embed the ipython kernel / REPL
into a QT Widget

Updated to use a RichJupyterWidget
"""

from PyQt4 import QtGui
from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager


def embed_ipy(parent, passthrough=None):
    """
    Embed an ipython kernel into the parent widget using a RichJupyterWidget
    :param parent: Qt Widget to receive the RichJupyterWidget
    :param passthrough: dict containing variables to pass into scope of the IPython Kernel
            Use this with caution; strange things can happen if you pass GUI elements to the IPython scope
            and then call any of their show() or draw() methods.
    :return: dict with reference to jupyter widget and ipython kernel
    """
    kernel_manager = QtInProcessKernelManager()
    kernel_manager.start_kernel()
    kernel = kernel_manager.kernel
    kernel.gui = 'qt4'

    kernel_client = kernel_manager.client()
    kernel_client.start_channels()
    kernel_client.namespace = parent

    def stop():
        kernel_client.stop_channels()
        kernel_manager.shutdown_kernel()

    layout = QtGui.QVBoxLayout(parent)
    widget = RichJupyterWidget(parent=parent)
    layout.addWidget(widget)
    widget.kernel_manager = kernel_manager
    widget.kernel_client = kernel_client
    widget.exit_requested.connect(stop)
    ipython_widget = widget
    ipython_widget.show()
    kernel.shell.push({'widget': widget, 'kernel': kernel, 'parent': parent})

    # pass variables from main GUI environment into IPython Kernel namespace
    if passthrough is not None:
        kernel.shell.push(passthrough)
        # variables stored in this dict are now accessible in the IPython shell
    return {'widget': widget, 'kernel': kernel}
