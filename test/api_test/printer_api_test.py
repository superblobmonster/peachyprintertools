import unittest
import os
import sys
from StringIO import StringIO

from mock import patch

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

from domain.configuration_manager import ConfigurationManager
from api.print_api import PrintAPI
import test_helpers


class PrintAPITests(unittest.TestCase, test_helpers.TestHelpers):


    @patch('api.print_api.Controller')
    @patch('api.print_api.PathToAudio')
    @patch('api.print_api.HomogenousTransformer')
    @patch('api.print_api.AudioWriter')
    @patch('api.print_api.GCodeReader')
    @patch('api.print_api.AudioModulationLaserControl')
    @patch('api.print_api.DripBasedZAxis')
    def test_print_gcode_should_create_required_classes_and_start_it(self, 
            mock_DripBasedZAxis,
            mock_AudioModulationLaserControl,
            mock_GCodeReader,
            mock_AudioWriter,
            mock_Transformer,
            mock_PathToAudio,
            mock_Controller,
            ):
        gcode_path = "FakeFile"
        actual_samples_per_second = 7
        fake_layers = "Fake Layers"
        mock_dripbasedzaxis = mock_DripBasedZAxis.return_value
        mock_audiomodulationlasercontrol = mock_AudioModulationLaserControl.return_value
        mock_gcodereader = mock_GCodeReader.return_value
        mock_audiowriter = mock_AudioWriter.return_value
        mock_transformer = mock_Transformer.return_value
        mock_pathtoaudio = mock_PathToAudio.return_value
        mock_controller = mock_Controller.return_value

        mock_audiomodulationlasercontrol.actual_samples_per_second = actual_samples_per_second
        mock_gcodereader.get_layers.return_value = fake_layers

        api = PrintAPI(self.DEFAULT_CONFIG)
        api.print_gcode(gcode_path)

        mock_DripBasedZAxis.assert_called_with(
            drips_per_mm = self.DEFAULT_CONFIG['drips_per_mm'],
            initial_height = 0.0,
            sample_rate =  self.DEFAULT_CONFIG['input_sample_frequency'],
            bit_depth = self.DEFAULT_CONFIG['input_bit_depth']
            )
        mock_AudioModulationLaserControl.assert_called_with(
            self.DEFAULT_CONFIG['output_sample_frequency'],
            self.DEFAULT_CONFIG['on_modulation_frequency'],
            self.DEFAULT_CONFIG['off_modulation_frequency'],
            )
        mock_GCodeReader.assert_called_with(gcode_path)
        mock_AudioWriter.assert_called_with(
            self.DEFAULT_CONFIG['output_sample_frequency'],
            self.DEFAULT_CONFIG['output_bit_depth'],
            )
        mock_Transformer.assert_called_with(self.DEFAULT_CONFIG['calibration_data'], scale = self.DEFAULT_CONFIG['max_deflection'])
        mock_PathToAudio.assert_called_with(
            actual_samples_per_second,
            mock_transformer, 
            self.DEFAULT_CONFIG['laser_thickness_mm']
            )
        mock_Controller.assert_called_with(
            mock_audiomodulationlasercontrol,
            mock_pathtoaudio,
            mock_audiowriter,
            fake_layers,
            mock_dripbasedzaxis
            )

    def test_print_can_be_stopped_before_started(self):
        api = PrintAPI(self.DEFAULT_CONFIG)
        api.stop()

    @patch('api.print_api.Controller')
    @patch('api.print_api.PathToAudio')
    @patch('api.print_api.HomogenousTransformer')
    @patch('api.print_api.AudioWriter')
    @patch('api.print_api.GCodeReader')
    @patch('api.print_api.AudioModulationLaserControl')
    @patch('api.print_api.DripBasedZAxis')
    def test_get_status_calls_controller_status(self, 
            mock_DripBasedZAxis,
            mock_AudioModulationLaserControl,
            mock_GCodeReader,
            mock_AudioWriter,
            mock_Transformer,
            mock_PathToAudio,
            mock_Controller,):
        mock_audiomodulationlasercontrol = mock_AudioModulationLaserControl.return_value
        mock_audiomodulationlasercontrol.actual_samples_per_second = 7
        mock_controller = mock_Controller.return_value


        api = PrintAPI(self.DEFAULT_CONFIG)
        api.print_gcode("Spam")
        api.get_status()

        mock_controller.get_status.assert_called_with()

if __name__ == '__main__':
    unittest.main()