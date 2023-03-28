import os.path
import unittest

import tomotwin.embed_main
from tomotwin.modules.inference.embedor import Embedor
import numpy as np
from tomotwin.modules.inference.argparse_embed_ui import EmbedConfiguration, EmbedMode
import tempfile
from tomotwin.modules.inference.volumedata import VolumeDataset
import mrcfile
from unittest.mock import MagicMock

class DummyEmbedor(Embedor):

    def __init__(self):
        self.tomotwin_config={}

    def embed(self, volume_data: VolumeDataset) -> np.array:
        embeddings = np.random.randn(2,32)
        return embeddings

class TestsEmbedMain(unittest.TestCase):

    def test_embed_main(self):
        from tomotwin.embed_main import _main_ as embed_main_func
        tomo = np.random.randn(50, 50, 50).astype(np.float32)

        with tempfile.TemporaryDirectory() as tmpdirname:
            volume_path = os.path.join(tmpdirname, "vola.mrc")

            with mrcfile.new(volume_path) as mrc:
                mrc.set_data(tomo)
            tomotwin.embed_main.make_embeddor = MagicMock(return_value=DummyEmbedor())
            tomotwin.embed_main.get_window_size = MagicMock(return_value=37)
            embed_conf = EmbedConfiguration(
                model_path=None,
                volumes_path=volume_path,
                output_path=tmpdirname,
                mode=EmbedMode.TOMO,
                batchsize=3,
                stride=1,
                zrange=None
            )
            embed_main_func(embed_conf)
            self.assertEqual(True, os.path.exists(os.path.join(tmpdirname, "vola_embeddings.temb")))

    def test_embed_tomogram(self):
        from tomotwin.embed_main import embed_tomogram
        tomo = np.random.randn(50,50,50)
        with tempfile.TemporaryDirectory() as tmpdirname:
            embed_conf = EmbedConfiguration(
                model_path=None,
                volumes_path="my/fake/volume.mrc",
                output_path=tmpdirname,
                mode=None,
                batchsize=3,
                stride=1,
                zrange=None
            )
            embed_tomogram(
                tomo=tomo,
                embedor=DummyEmbedor(),
                window_size=10,
                conf=embed_conf
            )
            import os

            self.assertEqual(True, os.path.exists(os.path.join(tmpdirname,"volume_embeddings.temb")))

    def test_embed_subvolume(self):
        from tomotwin.embed_main import embed_subvolumes

        with tempfile.TemporaryDirectory() as tmpdirname:
            embed_conf = EmbedConfiguration(
                model_path=None,
                volumes_path="my/fake/volume.mrc",
                output_path=tmpdirname,
                mode=None,
                batchsize=3,
                stride=1,
                zrange=None
            )
            paths=[os.path.join(tmpdirname,"vola.mrc"),os.path.join(tmpdirname,"volb.mrc")]

            for p in paths:
                with mrcfile.new(p) as mrc:
                    mrc.set_data(np.random.rand(50, 50).astype(np.float32))


            embed_subvolumes(
                paths=paths,
                embedor=DummyEmbedor(),
                conf=embed_conf
            )
            self.assertEqual(True, os.path.exists(os.path.join(tmpdirname, "embeddings.temb")))

if __name__ == '__main__':
    unittest.main()
