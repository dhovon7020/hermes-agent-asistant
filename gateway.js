require('dotenv').config();
const { Bot } = require('grammy');
const axios = require('axios');
const http = require('http');

const server = http.createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('Hermes Nous Portal Gateway is Online 24/7!\n');
});
const PORT = process.env.PORT || 8080;
server.listen(PORT, '0.0.0.0', () => {
    console.log(`Hermes Live Server running on port ${PORT}`);
});

const bot = new Bot(process.env.TELEGRAM_BOT_TOKEN);
const ALLOWED_USER = parseInt(process.env.TELEGRAM_ALLOWED_USERS);

async function askHermesPortalGateway(userMessage) {
    try {
        const response = await axios.post('https://openrouter.ai', {
            model: process.env.DEFAULT_MODEL,
            messages: [
                { role: 'system', content: process.env.SYSTEM_PROMPT },
                { role: 'user', content: userMessage }
            ]
        }, {
            headers: {
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://github.com',
                'X-Title': 'Hermes Nous Portal Bot'
            },
            timeout: 25000
        });

        if (response.data && response.data.choices && response.data.choices.length > 0) {
            return response.data.choices.message.content.trim();
        }
        return "দুঃখিত এডাম, পোর্টাল গেটওয়ে কোনো সাড়া দেয়নি।";
    } catch (error) {
        return "হার্মিস পোর্টাল ক্লাস্টার অত্যন্ত ব্যস্ত। অনুগ্রহ করে আর একবার মেসেজ দিন।";
    }
}

bot.command('start', async (ctx) => {
    if (ctx.from.id !== ALLOWED_USER) return ctx.reply("দুঃখিত, আপনি অনুমোদিত নন।");
    await ctx.reply("হ্যালো এডাম! আমি NousResearch-এর অফিসিয়াল 'Hermes 3' এজেন্ট। আমি আপনার দেওয়া Nous Portal লিংকের সাথে সফলভাবে কানেক্ট হয়ে এখন ২৪/৭ সচল আছি! আমাকে বাংলায় যেকোনো প্রশ্ন করুন।");
});

bot.on('message:text', async (ctx) => {
    if (ctx.from.id !== ALLOWED_USER) return;
    await ctx.replyWithChatAction('typing');
    const reply = await askHermesPortalGateway(ctx.message.text);
    await ctx.reply(reply);
});

console.log("হার্মিস অফিসিয়াল পোর্টাল গেটওয়ে ব্যাকগ্রাউন্ডে চালু হচ্ছে...");
bot.start();
