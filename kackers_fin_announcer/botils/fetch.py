@tasks.loop(seconds=10)
async def fetch_fins(members):

@fetch_fins.before_loop
async def before():
  await client.wait_until_ready()

fetch_fins.start() #deplaced outside of the function