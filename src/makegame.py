import os
import glob

import pandas as pd

def collect_from_boxscores(path):
    """Collect people entries from boxscores repository.
    """
    print "Collecting items from boxscores dataset."
    dflist = []
    for sourcepath in glob.glob("%s/processed/*/*" % path):
        source = "/".join(sourcepath.split("/")[-2:])
        print "Collecting source %s" % source

        try:
            dflist.append(pd.read_csv("%s/games.csv" % sourcepath,
                                      dtype=str))
            dflist[-1]['source'] = "boxscores/%s" % source
        except IOError:
            print "  Warning: did not find games file"
    print
    return dflist

def main():
    games = pd.concat(collect_from_boxscores("../boxscores"),
                      ignore_index=True)
    games['league.year'] = games['date'].str[:4]
    games['league'] = games['league'].apply(lambda x: x + " League" if "Association" not in x else x)
    games.rename(inplace=True,
                 columns={'league':  'league.name',
                          'date':    'game.date',
                          'number':  'game.number',
                          'away':    'away.name',
                          'home':    'home.name',
                          'key':     'game.ref'})
    games.sort_values(['league.year', 'league.name',
                       'game.date', 'home.name', 'game.number'],
                       inplace=True)
    # We convert dates to YYYYMMDD. This way, ident files can be loaded
    # into e.g. Excel for editing, without messing up the formatting.
    # YYYYMMDD is considered a valid ISO date format as well.
    games['game.date'] = games['game.date'].str.replace("-", "")

    idents = []
    for identfile in glob.glob("games/*/*.csv"):
        print "Collecting identfile %s" % identfile
        idents.append(pd.read_csv(identfile, dtype=str))
    print
    if len(idents) > 0:
        idents = pd.concat(idents, ignore_index=True)

        # This merge is somewhat simpler than the people merge right
        # now, because we rely on all these data being from the
        # boxscore entry file format.
        games = pd.merge(games, idents[['ident', 'game.ref']],
                         how='left', on='game.ref')
    else:
        games['ident'] = None
    
    games = games[['source', 'league.year', 'league.name', 'ident',
                   'game.date', 'game.number',
                   'away.name', 'away.score', 'home.name', 'home.score',
                   'game.ref']]

    print "Writing ident files..."
    for ((year, league), data) in games.groupby(['league.year', 'league.name']):
        print year, league
        try:
            os.makedirs("games/%s" % year)
        except os.error:
            pass
        data.to_csv("games/%s/%s%s.csv" %
                    (year, year,
                     league.replace(" ", "").replace("-", "")),
                    index=False)

if __name__ == '__main__':
    main()
    

    
