from config import dp
from db.database import session
from db.models import Debt, Record
from db.CRUD.player import get_player_from_id
from resourses.keyboards import get_paid_button
from resourses.replies import answer


async def equalizer(debtors: list, creditors: list, game_id: int, transactions=[]) -> list[Debt]:
    # if transactions is None:
    #     transactions = []
    for debtor in debtors:
        for creditor in creditors:
            if abs(debtor[1]) == creditor[1]:
                debt = Debt(
                    game_id=game_id,
                    creditor_id=creditor[0],
                    debtor_id=debtor[0],
                    amount=creditor[1],
                )
                transactions.append(debt)
                debtors.remove(debtor)
                creditors.remove(creditor)
                return await equalizer(debtors, creditors, game_id)

    sorted_creditors = sorted(creditors, key=lambda x: x[1], reverse=True)
    sorted_debtors = sorted(debtors, key=lambda x: x[1])

    while sorted_debtors:
        if abs(sorted_debtors[0][1]) < sorted_creditors[0][1]:
            debt = Debt(
                game_id=game_id,
                creditor_id=sorted_creditors[0][0],
                debtor_id=sorted_debtors[0][0],
                amount=abs(sorted_debtors[0][1]),
            )
            transactions.append(debt)
            sorted_creditors[0][1] = sorted_creditors[0][1] - abs(sorted_debtors[0][1])
            del sorted_debtors[0]
            return await equalizer(sorted_debtors, sorted_creditors, game_id)
        else:
            debt = Debt(
                game_id=game_id,
                creditor_id=sorted_creditors[0][0],
                debtor_id=sorted_debtors[0][0],
                amount=sorted_creditors[0][1],
            )
            transactions.append(debt)
            sorted_debtors[0][1] = sorted_debtors[0][1] + sorted_creditors[0][1]
            del sorted_creditors[0]
            return await equalizer(sorted_debtors, sorted_creditors, game_id)
    return transactions


async def debt_calculator(game_id: int) -> list[Debt]:
    records = session.query(Record).filter(Record.game_id == game_id).all()
    creditors = [
        [record.player_id, record.net_profit]
        for record in records
        if record.net_profit > 0
    ]
    debtors = [
        [record.player_id, record.net_profit]
        for record in records
        if record.net_profit < 0
    ]
    transactions = await equalizer(debtors, creditors, game_id)
    return transactions


async def commit_debts_to_db(transactions: list[Debt]) -> None:
    for transaction in transactions:
        session.add(transaction)
    session.commit()
    session.close()


async def debt_informer_by_id(game_id: int) -> None:
    debts = session.query(Debt).filter(Debt.game_id == game_id).all()
    for debt in debts:
        creditor = await get_player_from_id(debt.creditor_id)
        debtor = await get_player_from_id(debt.debtor_id)
        await dp.bot.send_message(
            chat_id=debtor.telegram_id,
            text=answer['debtor_personal_game_report'].format(
                debt.game_id, debt.id, debt.amount / 100, '@' + creditor.username),
            reply_markup=await get_paid_button(debt.id),
        )
        await dp.bot.send_message(
            chat_id=creditor.telegram_id,
            text=answer['creditor_personal_game_report'].format(
                debt.game_id, debt.id, '@' + debtor.username, debt.amount / 100),
        )
