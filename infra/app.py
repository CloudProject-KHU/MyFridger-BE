import aws_cdk as cdk

from stacks.backend import BackendStack

from utils import Config

app = cdk.App()

backend_stack = BackendStack(app, "FridgerBackend")

app.synth()
