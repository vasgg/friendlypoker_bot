answer = {
    "start_reply": "<code>Greetings, {}.\n"
                   "Your ID: <b>{}</b>\n\n"
                   "If you come to play, just press </code>/game\n\n",
    # "For browse your statistics, go to /stats",
    "no_game_admin_reply": "<code>Welcome to administrative section.\n\n"
                           "You can start new game here</>",
    "players_reply": "<code>Enter missing id's separated by spaces, or 0 for next step</code>",
    "host_game": "<code>Who's hosted the game?</code>",
    "no_debt_game": "Game ending without any debts",
    "host_game_with_missing_players": "<code>Missing players id's: {}. Who's hosted the game?</code>",
    "on_game_admin_reply": "Welcome to the game!\n\n"
                           "Vot zdes srazu game stats output",
    "not_admin_reply": "<code>You are not allowed to view this section.\n\n"
                       "Administration.</code>",
    "game_menu_current_game": "Tut srazu huyak stata po current game",
    "game_menu_new_game": "<code>Game not started yet...</>\n",
    "current_game_stats_admin_reply": "<code>GAME {:02} IN PROGRESS.\n\n"
                                      "TABLE SIZE  : {}\n"
                                      "GAME STARTED: {}\n"
                                      "TOTAL POT   : {}\n"
                                      "ADMIN       : {}({})\n"
                                      "HOST        : {}({})</code>",
    "current_game_stats_player_reply": "<code>GAME {:02} IN PROGRESS.\n\n"
                                       "PLAYER ID   : {}\n"
                                       "GAME STARTED: {}\n\n"
                                       "YOUR BUY-IN : {}\n"
                                       "TOTAL POT   : {}</code>",
    "exited_game_stats_player_reply": "<code>LEAVING GAME {:02}.\n\n"
                                      "GAME DURATION    : {}\n"
                                      "YOUR BUY-IN      : {}\n"
                                      "YOUR BUY-OUT     : {}\n"
                                      "PROFIT           : {}\n"
                                      "ROI              : {}</code>",
    "exit_game_by_player_reply": "<code>Whats your remaining balance?</code>",
    "exit_game_wrong_total_sum": "<code>Impossible to finish the game, the buy-in and cash-out amounts do not match\n\n"
                                 "Difference: <b>{}</></code>",
    "value_error_reply": "Please enter correct value",
    "debtor_personal_game_report": "<code>GAME {:02}. DEBT REPORT #{}:</>\n\n"
                                   "You owe <b>{:.2f} GEL</> to {}.",
    "creditor_personal_game_report": "<code>GAME {:02}. DEBT REPORT #{}:</>\n\n"
                                     "{} owes you {:.2f} GEL.",
    "debt_marked_as_paid": "<code>GAME {:02}. DEBT REPORT #{}:</>\n\n"
                           "{} marked debt as paid. Amount: {:.2f} GEL.\n"
                           "Do you receive payment?",
    "debt_complete": "<code>GAME {:02}. DEBT REPORT #{}:</>\n\n"
                     "{} marked debt as completed.\n",
    "debt_incomplete": "<code>GAME {:02}. DEBT REPORT #{}:</>\n\n"
                       "{} marked debt as incompleted!\n",
    "global_game_report": "<code>GAME {:02} FINISHED.\n\n"
                          "GAME DURATION: {}\n"
                          "TOTAL PLAYERS: {}\n"
                          "TOTAL POT    : {}\n\n"
                          "HOST         : {}\n"
                          "MVP          : {}</>\n",
    "start_game_report": "<code>GAME {:02} IN PROGRESS</>.\n\n",
    "add_funds_report": "<code>GAME {:02} IN PROGRESS.\n\n"
                        "BUY-IN REPORT: YOU ADD 1000 FUNDS\n</>",
    "remaining_players_in_game": "<code>Can't close session,following players still in game:\n\n"
                                 "{}</>",
}
