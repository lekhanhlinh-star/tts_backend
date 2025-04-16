import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from BreezyVoice.single_inference import single_inference,CustomCosyVoice,G2PWConverter



class ZeroShotTts:
    
    def __init__(self,model_path:str):
        self.cosyvoice = CustomCosyVoice(model_path)
        self.bopomofo_converter = G2PWConverter()
        
        
    def synthesize(self,speaker_prompt_audio_path:str,output_path:str,content_to_synthesize:str,speaker_prompt_text_transcription:str=None):
        file_save_path=single_inference(
                    speaker_prompt_audio_path=speaker_prompt_audio_path,
                    content_to_synthesize=content_to_synthesize,
                    speaker_prompt_text_transcription=speaker_prompt_text_transcription,
                    output_path=output_path,
                    cosyvoice=self.cosyvoice,
                    bopomofo_converter=self.bopomofo_converter,
                )
        return file_save_path

if __name__=="__main__":
    model = ZeroShotTts("/home/linh/tts-backend/app/BreezyVoice/pretrain_models")
    file_save = model.synthesize(
        "/home/linh/tts-backend/app/BreezyVoice/output.wav",
        "out.wav"
        "Hello",
    )
