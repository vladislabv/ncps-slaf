import torch.optim as optim

import pytorch_lightning as pl
from torchmetrics import MeanAbsolutePercentageError

class SequenceLearner(pl.LightningModule):
    """Class wrapper for training the models efficiently.
    Pay attention that we use here MAPE as loss variable.

    If you want to save the model itself into checkpoint,
    use `self.save_hyperparameters()`.
    """
    def __init__(self, model, lr=0.005, features_num=3, device="cuda"):
        super().__init__()
        self.save_hyperparameters(ignore=['model'])
        self.model = model
        self.features_num = features_num
        self.mydevice = device
        self.lr = lr

    def training_step(self, batch, batch_idx):
        x, y = batch
        x = x.to(self.mydevice)
        y = y.to(self.mydevice)
        x = x.view((1, -1, self.features_num))
        y = y.view((1, -1, 1))
        
        mape = MeanAbsolutePercentageError().to(self.mydevice)
        
        y_hat, _ = self.model.forward(x)
        y_hat = y_hat.view_as(y)
        loss = mape(y_hat, y)

        self.log("train_loss", loss, prog_bar=True)
        return {"loss": loss}

    def validation_step(self, batch, batch_idx):
        x, y = batch
        x = x.to(self.mydevice)
        y = y.to(self.mydevice)
        x = x.view((1, -1, self.features_num))
        y = y.view((1, -1, 1))
        
        mape_loss = MeanAbsolutePercentageError().to(self.mydevice)
        
        y_hat, _ = self.model.forward(x)
        y_hat = y_hat.view_as(y)
        loss = mape_loss(y_hat, y)

        self.log("val_loss", loss, prog_bar=True)
        return loss

    def test_step(self, batch, batch_idx):
        # Here we just reuse the validation_step for testing
        return self.validation_step(batch, batch_idx)

    def configure_optimizers(self):
        return optim.Adam(self.model.parameters(), lr=self.lr)