from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton

from bot.handlers import data
from parser.sms.utils import mapper
from db.transfer import LeadGenResult, LeadGenResultStatus


def _get_lead_status(status: str):
    return {
        LeadGenResultStatus.PROGRESS: "⬆",
        LeadGenResultStatus.FAILED: "🚫",
        LeadGenResultStatus.SUCCESS: "✅",
    }[status]


def _get_button_action(status: LeadGenResultStatus):
    return {
        LeadGenResultStatus.FAILED: data.LeadCallbackAction.VIEW_ERROR,
    }.get(status, "")


def generate_leads_statuses_kb(leads: list[LeadGenResult]):
    kb, kb_line = [], []

    for result_id, result in enumerate(leads):
        if result_id % 2 == 0:
            kb.append(kb_line)
            kb_line = []

        action = _get_button_action(status=result.status)

        kb_line.append(InlineKeyboardButton(
            text=f"{_get_lead_status(status=result.status)} "
                 f"#{result.lead_id} | "
                 f"{result.ref_link}",
            callback_data=data.LeadStatusCallbackData(
                session_id=result.session_id,
                lead_id=result.lead_id,
                action=action
            ).pack()
        ))

    kb.append(kb_line)

    kb.append([
        InlineKeyboardButton(
            text="♻Рестарт сессии",
            callback_data=data.RestartSessionData(
                session_id=leads[0].session_id
            ).pack(),
        ),
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=kb
    )


def get_session_presets_kb(
    current_sms_service: str = mapper.HELPERSMS.KEY,
):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"{
                "🚩" if current_sms_service == mapper.SMSHUB.KEY else ""
                }☎ Sms-Hub",
                callback_data=data.SMSServiceSelectorData(
                    sms_service=mapper.SMSHUB.KEY
                ).pack()
            ), InlineKeyboardButton(
                text=f"{
                "🚩" if current_sms_service == mapper.HELPERSMS.KEY else ""
                }☎ Helper",
                callback_data=data.SMSServiceSelectorData(
                    sms_service=mapper.HELPERSMS.KEY
                ).pack()
            )],
        ]
    )
