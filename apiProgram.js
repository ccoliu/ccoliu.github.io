const OpenAI = require("openai");

const openai = new OpenAI();

async function main() {
  const completion = await openai.chat.completions.create({
    messages: [{ role: "system", content: "You are very good at coding and always gives good suggestion to people's source code at all degrees from coding style and correctness" },
    { role: "user", content: "which source is better" },
    { role: "user", content: "for ( int i = 0 ; i <10;i++ ) {cout<< \"HI\"; }" },
    { role: "user", content: "for ( int i = 0 ; i < 10 ; i++ ) { cout<< \"HI\"; }" }],
    model: "gpt-3.5-turbo",
    max_tokens: 150,
  });

  console.log(completion.choices[0]);
}

main();