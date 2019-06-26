from ipykernel.kernelapp import IPKernelApp
from .kernel import KismetKernel

IPKernelApp.launch_instance(kernel_class=KismetKernel)
