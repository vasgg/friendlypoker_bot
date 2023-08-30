answer = {
    'start_reply': 'Greetings, {}.\n'
                   'Your ID: <b>{}</b>\n\n'
                   'If you come to play, just press /game\n\n',
    # 'For browse your statistics, go to /stats',
    'settings_reply': 'game settings menu',
    'promote_reply': 'Enter player ID for promoting to admin:\n\n',
    'demote_reply': 'Enter player ID for demoting from admin:\n\n',
    'promote_complete_reply': '{} is admin now',
    'demote_complete_reply': '{} is not admin now',
    'demote_error_reply': "You can't demote superadmin",
    'promote_complete_reply_to_player': '{} promoted you to admin role',
    'demote_complete_reply_to_player': '{} demoted you from admin role',
    'no_game_admin_reply': 'Welcome to administrative section.\n\n'
                           'You can start new game here',
    'players_reply': 'Enter missing ids separated by spaces, or 0 for next step',
    'no_debt_game': 'Game ending without any debts',
    'not_admin_reply': 'You are not allowed to view this section.\n\n'
                       'Administration.',
    'game_menu_new_game': 'Game not started yet...\n',
    'current_game_stats_admin_reply': '<code>GAME {:02} IN PROGRESS.\n\n'
                                      'GAME STARTED: {}\n'
                                      'TOTAL POT   : {}\n'
                                      'ADMIN       : {}\n</code>',
    'current_game_stats_player_reply': '<code>GAME {:02} IN PROGRESS.\n\n'
                                       'PLAYER ID   : {}\n'
                                       'GAME STARTED: {}\n\n'
                                       'YOUR BUY-IN : {}\n'
                                       'TOTAL POT   : {}</code>',
    'exited_game_stats_player_reply': '<code>LEAVING GAME {:02}.\n\n'
                                      'GAME DURATION    : {}\n'
                                      'YOUR BUY-IN      : {}\n'
                                      'YOUR BUY-OUT     : {}\n'
                                      'PROFIT           : {}\n'
                                      'ROI              : {}</code>',
    'exit_game_by_player_reply': 'Whats your remaining balance?',
    'exit_game_wrong_total_sum': 'Impossible to finish the game, the buy-in and cash-out amounts do not match\n\n'
                                 'Difference: <b>{}</>',
    'value_error_reply': 'Please enter correct value',
    'debtor_personal_game_report': '<code>GAME {:02}. DEBT REPORT #{}:</>\n\n'
                                   'You owe <b>{:.2f} GEL</> to {}.',
    'creditor_personal_game_report': '<code>GAME {:02}. DEBT REPORT #{}:</>\n\n'
                                     '{} owes you {:.2f} GEL.',
    'debt_marked_as_paid': '<code>GAME {:02}. DEBT REPORT #{}:</>\n\n'
                           '{} marked debt as paid. Amount: {:.2f} GEL.\n'
                           'Do you receive payment?',
    'debt_complete': '<code>GAME {:02}. DEBT REPORT #{}:</>\n\n'
                     '{} marked debt as completed.\n',
    'debt_incomplete': '<code>GAME {:02}. DEBT REPORT #{}:</>\n\n'
                       '{} marked debt as incompleted!\n',
    'global_game_report': '<code>GAME {:02} FINISHED.\n\n'
                          'GAME DURATION: {}\n'
                          'TOTAL POT    : {}\n\n'
                          'MVP          : {}</>\n',
    'start_game_report': '<code>GAME {:02} IN PROGRESS</>.\n\n',
    'add_funds_report': '<code>GAME {:02} IN PROGRESS.\n\n'
                        'BUY-IN REPORT: YOU ADD 1000 FUNDS\n</>',
    'remaining_players_in_game': '<code>Cant close session,following players still in game:\n\n'
                                 '{}</>',
    'value_error_log': 'User [{}] get error [{}] with data [{}]',
}
