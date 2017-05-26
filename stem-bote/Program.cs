using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Timers;
using Discord;
using System.IO;
using System.Text.RegularExpressions;
using System.Diagnostics;
using System.Threading;
using Argotic.Common;
using Argotic.Syndication;

namespace stembote
{
    class stembote
    {
        static void Main(string[] args) => new stembote().Start();

        public static DiscordClient _client = new DiscordClient();
        public static List<User> users = new List<User>();

        public void Start()
        {
            System.Timers.Timer caryCheckTimer = new System.Timers.Timer();
            caryCheckTimer.Elapsed += new ElapsedEventHandler(caryVideoChecker);
            caryCheckTimer.Interval = 60000;
            caryCheckTimer.Enabled = true;

            System.Timers.Timer abaCheckTimer = new System.Timers.Timer();
            abaCheckTimer.Elapsed += new ElapsedEventHandler(abaVideoChecker);
            abaCheckTimer.Interval = 60000;
            abaCheckTimer.Enabled = true;

            _client.Log.Message += (s, e) => Console.WriteLine($"[{e.Severity}] {e.Source}: {e.Message}");

            _client.MessageReceived += async (s, e) =>
            {
                string p = "sb?"; // define prefix variable

                bool isCmd = false;
                if (e.Message.Text.StartsWith(p + p))
                    isCmd = false; // if message has the prefix two (or more) times, set isCmd to false
                else if (e.Message.Text.StartsWith(p))
                    isCmd = true; // otherwise, if there's only one prefix, set isCmd to true
                                  // ^ this is a hacky solution but it works

                bool isOwner = e.User.Id == 140564059417346049; // test if user is the owner of the bot
                string msg = e.Message.Text; // grab contents of message
                string rawmsg = e.Message.RawText; // grab raw contents of message

                var msgarray = msg.Replace(p, "").Split(' ');
                string cmd = msgarray.FirstOrDefault().ToString();
                List<string> args = msgarray.Skip(1).ToList();

                var argtext = msg.Replace(p + cmd + "", "");
                if (msg.Contains(p + cmd + " "))
                    argtext = msg.Replace(p + cmd + " ", "");

                if (!e.Channel.IsPrivate)
                {
                    if (isCmd && e.Channel.Id == 282500390891683841)
                    {
                        if (cmd == "help")
                        {
                            string help = $"`{p}help` - lists the bot commands";
                            string usercount = $"`{p}usercount` - lists the users on the server"; // note: this command won't work unless joinbot is running
                            string userinfo = $"`{p}userinfo` - displays info about yourself or a mentioned user";
                            string serverinfo = $"`{p}serverinfo` - displays info about the server";
                            string roll = $"`{p}roll [# of sides] [# of dice to roll]` - rolls some dice";
                            string randomuser = $"`{p}randomuser` - selects a random user on the server";

                            string yt = $"`{p}yt [on/off]` - turn YT video notifications on/off";

                            string cmds = $"\n{help}\n{usercount}\n{userinfo}\n{serverinfo}\n{roll}\n{randomuser}";
                            string greet = "Hi! I'm the STEM part of the HTC-Bote, a super-exclusive part only for the HTwins STEM server. ";
                            string avacmds = $"I have a couple commands you can try out, which include: {cmds}\nI also have some commands for use in private messages: \n{yt}";

                            string helpmsg = greet + avacmds;
                            await e.Channel.SendMessage(helpmsg);
                        }
                        else if (cmd == "usercount")
                            await e.Channel.SendMessage($"`{e.Server.Name}` currently has {e.Server.UserCount} users.");
                        else if (cmd == "userinfo")
                        {
                            users = e.Server.Users.OrderBy(user => user.JoinedAt).ToList(); // refresh user cache for later on

                            // find user

                            User usr = e.User;
                            var txtsearch = e.Server.FindUsers(argtext, false).FirstOrDefault();

                            if (e.Message.MentionedUsers.FirstOrDefault() != null) // checks if there's a mentioned user
                                usr = e.Message.MentionedUsers.FirstOrDefault(); // updates 'usr' to be the mentioned user
                            else if (argtext != "")
                            {
                                if (txtsearch != null)
                                    usr = txtsearch;
                            }
                            // else if(e.Server.GetUser(Convert.ToUInt64(argtext)) != null)
                            // usr = e.Server.GetUser(Convert.ToUInt64(argtext));

                            // get user info

                            ulong id = usr.Id;
                            string username = clearformatting(usr.Name);
                            string discrim = $"#{usr.Discriminator}";

                            string nickname = "[none]";
                            if (!string.IsNullOrWhiteSpace(usr.Nickname))
                                nickname = clearformatting(usr.Nickname);

                            string game;
                            // string status = usr.Status.ToString();

                            if (usr.CurrentGame == null)
                                game = "[none]";
                            else
                            {
                                game = clearformatting(usr.CurrentGame.GetValueOrDefault().Name);
                                string streamUrl = usr.CurrentGame.GetValueOrDefault().Url;
                                //if (usr.CurrentGame.GetValueOrDefault().Url != null)
                                //    status = $"streaming # {streamUrl}";
                            }

                            DateTime joined = usr.JoinedAt;
                            var joinedDays = DateTime.Now - joined;
                            DateTimeOffset created = CreationDate(usr.Id);
                            var createdDays = DateTime.Now - created;
                            string avatar = usr.AvatarUrl;

                            //	int usercount = 0;
                            //	int memnum = 0;
                            //	while (memnum == 0)
                            //	{
                            //		usercount++;
                            //		User currentuser = users.ElementAt (usercount);
                            //		if(e.User == currentuser)
                            //			memnum = usercount;
                            //	}

                            // send message

                            await e.Channel.SendMessage($"```ini\n" +
                                $"\n[ID]            {id}\n" +
                                $"[Username]      {username}\n" +
                                $"[Discriminator] {discrim}\n" +
                                $"[Nickname]      {nickname}\n" +
                                $"[Current game]  {game}\n" +
                                // $"[Status]        {status}\n" +
                                $"[Joined]        {joined} ({joinedDays.Days} days ago)\n" +
                                $"[Created]       {created.ToString().Replace(" +00:00", "")} ({createdDays.Days} days ago)\n" +
                                //$"[Member #]      {memnum}\n" +      | broken for some reason. often shows users as being member #11
                                $"[Avatar] {avatar}\n```");
                        }
                        else if (cmd == "serverinfo")
                        {
                            var Roles = e.Server.Roles;
                            List<string> rolesList = new List<string>();
                            foreach (Role role in Roles)
                                rolesList.Add(role.Name);

                            DateTimeOffset created = CreationDate(e.Server.Id);
                            var createdDays = DateTime.Now - created;
                            string rolesString = string.Join(", ", rolesList.ToArray());
                            string region = e.Server.Region.Name;

                            await e.Channel.SendMessage($"```ini\n" +
                                $"[Name]            {clearformatting(e.Server.Name)}\n" +
                                $"[ID]              {e.Server.Id}\n" +
                                $"[User Count]      {e.Server.UserCount}\n" +
                                $"[Channel Count]   {e.Server.ChannelCount}\n" +
                                $"[Default Channel] #{e.Server.DefaultChannel}\n" +
                                $"[Role Count]      {e.Server.RoleCount}\n" +
                                $"[Roles]           {clearformatting(rolesString)}\n" +
                                $"[Owner]           @{clearformatting(e.Server.Owner.ToString())}\n" +
							    $"[Created]         {created.ToString().Replace(" +00:00", "")} ({createdDays.Days} days ago)\n" +
                                $"[Icon] {e.Server.IconUrl}\n" +
                                $"```");
                        }
                        else if (cmd == "roll")
                        {
                            try
                            {
                                Random random = new Random(); // Generate some randomness
                                string output = $"The 6-sided die rolled a {random.Next(1, 7)}."; // Define default output

                                if (args.Count == 2) // tests if there are two arguments
                                {
                                    if (args[1] != null)
                                    {
                                        int sides = int.Parse(args[0]); // Set die sides
                                        int dice = int.Parse(args[1]); // Set # of dice to roll

                                        int maxRolls = sides + 1; // Set max roll int
                                        if ((dice < 1) || (sides < 1)) // check if # of dice/die sides is under 1
                                            output = $"Yeahh, sorry, but you can't roll something that doesn't exist.";
                                        else if (sides == 1)
                                            output = $"All {dice} of the 1-sided dice shockingly rolled a 1."; // Change output if first arg was 1
                                        else if (dice <= 30)
                                        {
                                            if (sides <= 100)
                                            {
                                                int rollTracker = dice; // Create new variable to track the number of rolls left
                                                string rolledDice = ""; // Set blank string for the dice rolled
                                                while (rollTracker > 0) // If there are still dice to roll...
                                                {
                                                    if (rollTracker > 1) /// ...and it's not only one die...
                                                        rolledDice += $"{random.Next(1, maxRolls)}, "; // ... add a random roll to the roledDice string
                                                    else // or, if there is only one die left
                                                        rolledDice += $"and {random.Next(1, maxRolls)}"; // add the final random roll

                                                    rollTracker--; // subtract one die left to roll from roleTracker
                                                }
                                                output = $"The {dice} {sides}-sided dice rolled {rolledDice}."; // set output
                                            }
                                            else
                                                output = $"Woahh, that's a lot of sides. Try lowering it below 100?";
                                        }
                                        else
                                            output = "Woahh, that's a lot of dice to roll. Try lowering it below 30?"; // display error message because 30 rolls = lots of spam
                                    }
                                }
                                else if (args.Count == 1)
                                {
                                    if (args[0] != null)
                                    {
                                        int sides = int.Parse(args[0]); // Set die sides
                                        int maxRolls = sides + 1; // Set max roll int
                                        if (sides < 1)
                                            output = $"Yeahh, sorry, but you can't roll something that doesn't exist.";
                                        else if (maxRolls == 2)
                                            output = "The 1-sided die shockingly rolled a 1."; // Change output if first argument was "1"
                                        else
                                        {
                                            output = $"The {sides}-sided die rolled a {random.Next(1, maxRolls)}."; // Set the output message

                                            // hey, you! yes, you, reading this! don't you dare tell people about these easter eggs! i will be watching...
                                            if (sides == 666)
                                                output = $"Satan rolled a nice {random.Next(1, maxRolls)} for you.";
                                            else if (sides == 1337)
                                                output = $"Th3 {sides}-51d3d d13 r0ll3d 4 {random.Next(1, maxRolls)}.";
                                            else if (sides == e.Server.UserCount)
                                            {
                                                if (users.Count == 0)
                                                {
                                                    users = e.Server.Users.OrderBy(user => user.JoinedAt).ToList();
                                                    Thread.Sleep(500);
                                                }

                                                int rndNumber = random.Next(1, maxRolls);
                                                string rndUser = users.ElementAt(rndNumber).Name;
                                                output = $"{e.Server.UserCount}? That's how many users are on the server! Well, your die rolled a {random.Next(1, maxRolls)}, and according to the cache, that member is `{rndUser}`.";
                                            }
                                        }
                                    }
                                }

                                await e.Channel.SendMessage(output);
                            }
                            catch (Exception error)
                            {
                                Console.WriteLine($"[ERROR] Something happened while running {p}{cmd}: \n{error.ToString()}");
                                await e.Channel.SendMessage($"An error occured while trying to roll the dice. You most likely entered non-integers.");
                            }
                        }
                        else if (cmd == "randomuser")
                        {
                            Random random = new Random();

                            if (users.Count == 0)
                            {
                                users = e.Server.Users.OrderBy(user => user.JoinedAt).ToList(); // cache users if not already cached
                            }

                            int rndNumber = random.Next(1, e.Server.UserCount + 1);

                            try
                            {
                                string rndUser = users.ElementAt(rndNumber).Name;
                                await e.Channel.SendMessage($"Your random user of the day is {rndUser}, who was the {rndNumber} member to join the server.");
                            }
                            catch (Exception error)
                            {
                                Console.WriteLine($"[ERROR] Something happened while running {p}{cmd}: \n{error.ToString()}");
                                if (rndNumber > e.Server.UserCount)
                                    await e.Channel.SendMessage($"Something happened while trying to grab information about user #{rndNumber}, which seems to be bigger than the current user count ({e.Server.UserCount}) - good job <@140564059417346049> \ud83d\udc4f");
                                else
                                    await e.Channel.SendMessage($"Something happened while trying to grab information about user #{rndNumber}.");
                            }
                        }
                        else if (cmd == "debug" && isOwner)
                        {
                            var roles = e.Server.Roles.OrderBy(role => role.Position).ToList();
                            var rolestring = "Sever roles: ";
                            foreach (Role role in roles)
                            {
                                rolestring += role.Name + " | ";
                            }
                            Console.WriteLine(rolestring);
                        }
                    }
                }

                bool isHSTEM = false;
                if (e.Server != null)
                    if (e.Server.Id == 282219466589208576)
                        isHSTEM = true;

                if (cmd == "yt" && (isHSTEM || e.Channel.IsPrivate))
                {
                    if (_client.GetServer(282219466589208576).GetUser(e.User.Id) == null)
                        await e.Channel.SendMessage($"You must be on HTwins STEM to use this command. You can join it here: https://discord.gg/4Gn4GAC");

                    else if (args.Count == 1)
                    {
                        var hstem = _client.GetServer(282219466589208576);
                        var huser = hstem.GetUser(e.User.Id);
                        var role = hstem.GetRole(289942717419749377);

                        if (args[0] == "on")
                        {
                            await huser.AddRoles(role);
                            await e.Channel.SendMessage($"You have been given the YouTube notification role on HTwins STEM.");
                        }
                        else if (args[0] == "off")
                        {
                            await huser.RemoveRoles(role);
                            await e.Channel.SendMessage($"You have been removed from the YouTube notification role on HTwins STEM.");
                        }
                    }

                    else
                        await e.Channel.SendMessage($"Proper usage: `{p}yt [on/off]`");
                }
            };

            _client.UserJoined += (s, e) =>
            {
                if (e.Server.Id == 282219466589208576)
                    users.Add(e.User);
            };

            _client.UserLeft += (s, e) =>
            {
                if (e.Server.Id == 282219466589208576)
                    users.Remove(e.User);
            };

            string token = File.ReadAllText("token.txt");
            _client.ExecuteAndWait(async () =>
            {
                await _client.Connect(token, TokenType.Bot);
                Console.WriteLine($"Connected as {_client.CurrentUser.Name}#{_client.CurrentUser.Discriminator}");
            });

        }

        private static void caryVideoChecker(object source, ElapsedEventArgs e)
        {
            SyndicationResourceLoadSettings settings = new SyndicationResourceLoadSettings();
            settings.RetrievalLimit = 1;
    
            Uri feedUrl = new Uri("https://www.youtube.com/feeds/videos.xml?user=carykh");
            AtomFeed feed = AtomFeed.Create(feedUrl, settings);
            var videos = feed.Entries;
    
            bool alreadyPosted = false;
    
            if (videos.Count() == 0)
                Console.WriteLine("[Error] Feed contained no information.");
    
            foreach (var video in videos)
            {
	    		try
	    		{
	    			string videoUrlsFile = Directory.GetCurrentDirectory() + "/videoUrls.txt"; // String for the video URLS to check if a post is new, uses "videoUrls.txt" in directory the .exe is run from by default
	    			var logFile = File.ReadAllLines(videoUrlsFile);
	    			List<string> videoUrls = new List<string>(logFile);
    
	    			string newVideoUrl = video.Links.FirstOrDefault().Uri.ToString();
	    			string videoTitle = video.Title.Content;
    
	    			foreach (var videoUrl in videoUrls)
	    			{
	    				if (newVideoUrl == videoUrl)
	    				{
	    					alreadyPosted = true;
	    				}
	    			}
    
	    			try
	    			{
	    				if (alreadyPosted == false)
	    				{
                            string vidinfo = $"\"{videoTitle}\" - {newVideoUrl}";

	    					Console.WriteLine($"Found new video URL - {vidinfo} - Sending to discord");
    
	    					using (StreamWriter text = File.AppendText(videoUrlsFile))
	    						text.WriteLine(newVideoUrl);
    
	    					_client.GetChannel(282225245761306624).SendMessage($"@here `carykh` has uploaded a new YouTube video!\n {vidinfo}");
	    				}
	    			}
	    			catch (Exception error)
	    			{
	    				Console.WriteLine($"[Error] Bot ran into an issue while trying to post the video to discord. {error.ToString()}");
	    			}
	    		}
	    		catch (Exception error)
	    		{
	    			Console.WriteLine("[Error] An error occured during the video check -" + error.ToString());
	    		}
            }
    
        }
    
        private static void abaVideoChecker(object source, ElapsedEventArgs e)
        {
            SyndicationResourceLoadSettings settings = new SyndicationResourceLoadSettings();
            settings.RetrievalLimit = 1;
    
            Uri feedUrl = new Uri("https://www.youtube.com/feeds/videos.xml?user=1abacaba1");
            AtomFeed feed = AtomFeed.Create(feedUrl, settings);
            var videos = feed.Entries;
    
            bool alreadyPosted = false;
    
            if (videos.Count() == 0)
                Console.WriteLine("[Error] Feed contained no information.");
    
            foreach (var video in videos)
            {
                string videoUrlsFile = Directory.GetCurrentDirectory() + "/videoUrls.txt"; // String for the video URLS to check if a post is new, uses "videoUrls.txt" in directory the .exe is run from by default
                var logFile = File.ReadAllLines(videoUrlsFile);
                List<string> videoUrls = new List<string>(logFile);
    
                string newVideoUrl = video.Links.FirstOrDefault().Uri.ToString();
                string videoTitle = video.Title.Content;
    
                foreach (var videoUrl in videoUrls)
                    if (newVideoUrl == videoUrl)
                        alreadyPosted = true;
    
                try
                {
	    				if (alreadyPosted == false)
	    				{
                            string vidinfo = $"\"{videoTitle}\" - {newVideoUrl}";

	    					Console.WriteLine($"Found new video URL - {vidinfo} - Sending to discord");
    
	    					using (StreamWriter text = File.AppendText(videoUrlsFile))
	    						text.WriteLine(newVideoUrl);
    
	    					_client.GetChannel(282225245761306624).SendMessage($"@here `abacaba` has uploaded a new YouTube video!\n {vidinfo}");
	    				}
                }
                catch (Exception error)
                {
                    Console.WriteLine($"[Error] Bot ran into an issue while trying to post the video to discord. {error.ToString()}");
                }
            }
    
        }
        public static string clearformatting(string input)
        {
            var output = "[empty string]";
            if (!string.IsNullOrWhiteSpace(input))
                output = input.Replace("`", "​`").Replace("*", "​*").Replace("_", "​_").Replace("‮", " ");
            return output;
        }
        public static DateTimeOffset CreationDate(ulong id)
        {
			return DateTimeOffset.FromUnixTimeMilliseconds((Convert.ToInt64(id) >> 22) + 1420070400000);
        }
    }
}
