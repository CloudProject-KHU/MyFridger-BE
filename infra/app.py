import aws_cdk as cdk

from stacks.backend import BackendStack
# from stacks.receipt import ReceiptAnalysisStack

from utils import Config

env = cdk.Environment(
    account=Config.get("Account"),
    region=Config.get("Region")
)
app = cdk.App()

BackendStack(app, "FridgerBackend", env=env)
# ReceiptAnalysisStack(app, "ReceiptAnalysis", env=env)

app.synth()
