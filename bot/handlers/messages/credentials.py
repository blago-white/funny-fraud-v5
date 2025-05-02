from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import File, Message

from container import BotInstanceContainer
from bot.states.forms import CredentialsFileSettingForm


router = Router(name=__name__)


@router.message(F.text == "🔠 Изменить файл строк")
async def make_update_credentials(message: Message, state: FSMContext):
    await state.set_state(CredentialsFileSettingForm.wait_file)

    await message.reply("🔄 Отправьте файл .xlsx")


@router.message(CredentialsFileSettingForm.wait_file)
async def upload_credentials(message: Message, state: FSMContext):
    bot = BotInstanceContainer().bot

    try:
        file_id = message.document.file_id
        file_info = await bot.get_file(file_id=file_id)
        file_path = file_info.file_path
    except:
        return await message.reply("❌ Похоже, файл не прикреплен")

    download_path = 'data/credentials.xlsx'

    await bot.download_file(file_path, download_path)

    await state.clear()

    await message.reply("✅ <b>Записано!</b>")
