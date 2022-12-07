module.exports = async function (context) {
  console.log(context.request.body);
  let obj = context.request.body;
  return {
    status: 200,
    body: "NF_EXECUTED " + JSON.stringify(obj),
  };
};
