import torch
import torch.nn as nn
import torch.optim as optim

import pytorch_lightning as pl


class SequenceLearner(pl.LightningModule):
    # LightningModule for training a RNNSequence module
    # TODO: Iterieren Tag"
    # Cycle 0"
    # VITALI: Lücken schließen, Wochentage, Feiertage"
    # Alle Indizes müssen mit 24 multipliziert werden, da wir stündliche Auflösung haben"
    # Iteration 0: y_(-1) , y_(-7) , y_(-365) -> y_hat(0) V y_(0)"
    # Iteration 1: y_hat(0) , y_(-6) , y_(-364) -> y_hat(1) V y_(1)"
    # Iteration 2: y_hat(1) , y_(-5) , y_(-363) -> y_hat(2) V y_(2)"
    # ..."
    # Iteration 6: y_hat(5) , y_(-1) , y_(-359) -> y_hat(6) V y_(6)"
    # Cycle 1"
    # Iteration 7: y_(6) , y_(0) , y_(-358) -> y_hat(7) V y_(7)
    # ...
    # Iteration 12: y_hat(5) , y_(6) , y_(-352) -> y_hat(12) V y_(12)
    # Modell speichern?"
    def __init__(self, model, lr=0.005):
        super().__init__()
        self.model = model
        self.lr = lr

    def training_step(self, batch, batch_idx):
        x, y = batch
        x = x.view((1, -1, 3))
        y = y.view((1, -1, 1))

        loss = 0.0

        for idx in range(x.shape[1]):
            # get current row
            x_curr = torch.index_select(x, 1, torch.tensor([idx]))
            y_curr = torch.index_select(y, 1, torch.tensor([idx]))
            y_hat, _ = self.model.forward(x_curr)

            y_hat = y_hat.view_as(y_curr)
            loss += nn.MSELoss()(y_hat, y_curr)

            try:
                # replace y true with prediction
                x[0, idx + 1, 0] = y_hat.item()
            except IndexError:
                # last element of the batch reached
                pass

        self.log("train_loss", loss/y.shape[1], prog_bar=True)
        return {"loss": loss}

    def validation_step(self, batch, batch_idx):
        x, y = batch
        x = x.view((1, -1, 3))
        y = y.view((1, -1, 1))
        
        loss = 0.0

        for idx in range(x.shape[1]):
            # get current row
            x_curr = torch.index_select(x, 1, torch.tensor([idx]))
            y_curr = torch.index_select(y, 1, torch.tensor([idx]))
            y_hat, _ = self.model.forward(x_curr)
            y_hat = y_hat.view_as(y_curr)

            loss += nn.MSELoss()(y_hat, y_curr)

            try:
                # replace y true with prediction
                x[0, idx + 1, 0] = y_hat.item()
            except IndexError:
                # last element of the batch reached
                pass

        self.log("val_loss", loss/y.shape[1], prog_bar=True)
        return loss

    def test_step(self, batch, batch_idx):
        # Here we just reuse the validation_step for testing
        return self.validation_step(batch, batch_idx)

    def configure_optimizers(self):
        return optim.Adam(self.model.parameters(), lr=self.lr)