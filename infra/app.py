import aws_cdk as cdk

from stacks.backend import BackendStack
# from stacks.receipt import ReceiptAnalysisStack

from utils import Config

app = cdk.App()

BackendStack(app, "FridgerBackend")
# ReceiptAnalysisStack(app, "ReceiptAnalysis", env=env)

app.synth()
