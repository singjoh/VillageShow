## Eynsham Village Show

#### Preparing for a new show

Add all the required Cups (CUPS tab), note that the cup KEY is required to be unique, but is only used for the import of the Class list.

Build a CSV file with all the Classes, in the following format:

| Class | Name | Description | Kids | Judge | Cup1 | Cup2 | Cup3 |
| ----- | ---- | ----------- | ---- | ----- | ---- | ---- | ----  |
| 1 | Bunch of Flowers | | N | Gardening | CHAMPION | | |
| 2 | Potatoes|3 Potatoes | N | Gardening | CHAMPION | POT | |
| 3 | Victoria Sponge | | N | Food | CHAMPION | VSPONGE | COOK |
| 4 | Garden on a Plate   | | N | Fun4All | CHAMPION | | |
| 50 | Garden on a Plate (4-7 ) | | Y|Kids | KIDSTOTAL | GOAP | |
| 51 | Garden on a Plate | | Y | Kids|KIDSTOTAL | GOAP | |

Save the file in c:/vshow/mounts/files/in

Note that Name + Kids flag is unique (so we need to give a new name to the (4-7) category).
In the above, we see the Gardening judge has two categories to check, both of which accumulate into the 'CHAMPION' Cup (i.e. there is a cup with that KEY), but only Potatoes category qualifies for the POT Cup.
The 'Name' is what appears on certificates.

Then use the IMPORT CLASSES action to load the data.

#### Entering Villagers and Entries

Use the Villagers page to create/find villagers and add entries.
Note that the villager's name combo box is searchable and allows direct create.  Typing in the box will show a filtered set from which one can be picked.  If the item is not their then press 'RETURN' and the item will be added to the list (but will still need to be picked ... the quickest way to do that is to press the Esc key).

Remember to Save as you go along.  

Use the GENERATE ENTRY KEYS action to assign unique codes to each entry.

#### Export the pre-show data

Use the EXPORT PRE-SHOW FILES action, this will place files in c:/vshow/mounts/files/out

To validate the data, check the entranst.docx and compare against the entry forms. If there are any errors then correct and regenerate the ENTRY KEYS. 
Then use mail-merge for stickers and labels.

#### Judging

The judges.docx has places for the judges/assistants to write in the ENTRY KEYS, these need to be copied into the JUDGES page.  The JUDGES page has validation so that only matching items can be entered into classes and cups.

#### Export the post-show data

Use the EXPORT POST-SHOW FILES action, this will place files in c:/vshow/mounts/files/out.

The files include the medal lists for the certificates, and some csv files to help check the data.

