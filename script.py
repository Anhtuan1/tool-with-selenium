SCRIPT_QUIT = '''
            function addQuitButton() {
                var existingButton = document.getElementById("quit-button");
                if (existingButton) {
                    return; // If the button already exists, don't add it again
                }

                var button = document.createElement("button");
                button.innerHTML = "Quit";
                button.id = "quit-button";
                document.body.appendChild(button);

                // Apply CSS styles to the button
                var css = `
                    #quit-button {
                        position: fixed;
                        top: 10px;
                        right: 10px;
                        padding: 15px 30px;
                        font-size: 20px;
                        background-color: rgba(255, 77, 77, 0.2); /* Red background with 0.2 opacity */
                        color: white;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                        z-index: 1000; /* Ensure it stays on top */
                    }

                    #quit-button:hover {
                        background-color: rgba(255, 26, 26, 0.4); /* Darker red on hover with higher opacity */
                    }
                `;
                var style = document.createElement('style');
                style.appendChild(document.createTextNode(css));
                document.head.appendChild(style);

                button.addEventListener("click", function() {
                    var facebookDiv = document.createElement("div");
                    facebookDiv.id = "facebook";
                    document.body.appendChild(facebookDiv);
                    window.close();
                });
            }


            // Add the button immediately
            addQuitButton();
        '''

SCRIPT_GAME_CONTROL_PAWS = """
(async function () {
    await startGame();
    setTimeout(async () => {
        await startTask();//start
        await startTask(7000);//claim
    }, 20000)
    
})();

async function startGame() {
	console.log('- startGame');
	return new Promise(resolve => {
		setTimeout(async () => {
            if(await checkExistElm(document.querySelectorAll("div.btn-next"), 'Let’s start')) {
                await clickByLabel(document.querySelectorAll("div.btn-next"), 'Let’s start', 20000, true);
            }
            await clickByLabel(document.querySelectorAll("div.btn-next"), 'Gotcha!', 2000, true);
            await clickByLabel(document.querySelectorAll(".connect-wallet-con div"), 'Connect wallet', 2000, true);
            await clickByLabel(document.querySelectorAll("button.connect-btn"), 'Connect your TON wallet', 3000);
            await clickByLabel(document.querySelectorAll('button'), "Open Wallet in Telegram", 2000);
            
            resolve();
		}, 2000);
	});
}

//mission
async function startTask(time = 2000) {
    console.log('- startTask');
	return new Promise((resolve) => {
		setTimeout(async () => {
			await clickByLabel(document.querySelectorAll(".nav-item-con div"), 'Earn', 2000, true);
		
			let tasks = document.querySelectorAll(".invite-item");
			if(tasks.length) {
				let taskIndex = 0;
				for await (let task of tasks) {
					taskIndex++;
                    let title = task.querySelector('.main-info .wallet-con .wallet').textContent;
					let taskBtn = task.querySelector('.start-btn');
					
					if(!title.includes('Invite')) {
						console.log('--- start task ', taskIndex, ':', title);
						
						//click got it to back
                        console.log('click:', taskBtn);
						await waitClick(taskBtn);
                        await waitClick(taskBtn);
                        await waitClick(taskBtn);
					}
				}				
			}
			resolve();
		}, time);
	});
}

async function getElementByText(elm_list, label, time = 0, must_same = false) {
	let result = null;
	if (elm_list.length && label) {
        for await (const elm of elm_list) {
            //console.log('--', elm.textContent, elm);
            if((!must_same && elm.textContent.includes(label)) || (must_same && elm.textContent == label)) {
                console.log('->', elm.textContent, elm);
                result = elm;
                break;
			}
        }
	}
	return new Promise(resolve => setTimeout(resolve(result), time));
}

async function checkExistElm(elmList, label, time = 0) {
	let result = false;
	if (elmList.length && label) {
		for (let btnItem of elmList) {
			if(btnItem.textContent.includes(label)){
                console.log('--- elm exist', btnItem);
                result = true;
				break;
			}
		}
	}
	return new Promise(resolve => setTimeout(resolve(result), time));
}

async function simulateMouseClick(el) {
  let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
  el.dispatchEvent(new MouseEvent("mousedown", opts));
  await new Promise(r => setTimeout(r, 50));
  el.dispatchEvent(new MouseEvent("mouseup", opts));
  el.dispatchEvent(new MouseEvent("click", opts));
}

//For React ≥ 15.6.1
async function simulateMouseInput(el, value) {
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
      window.HTMLInputElement.prototype,
      'value').set;
    nativeInputValueSetter.call(el, value);
    const event = new Event('input', { bubbles: true });
    el.dispatchEvent(event);
}

async function waitClick(btn, time = 1000) {
	if (btn) await simulateMouseClick(btn);
	return new Promise(resolve => setTimeout(resolve, time));
}
async function clickByLabel(btn_list, label, time = 1000, must_same = false) {
	if (btn_list.length && label) {
        for await (const btnItem of btn_list) {
            //console.log('--', btnItem.textContent, btnItem);
            if((!must_same && btnItem.textContent.includes(label)) || (must_same && btnItem.textContent == label)) {
                //console.log('->', btnItem.textContent, btnItem);
                await simulateMouseClick(btnItem);
                break;
			}
        }
	}
	return new Promise(resolve => setTimeout(resolve, time));
}
        """
SCRIPT_WALLET_CONTROL_PAWS = """
(async function () {
    await startConnect();
})();

async function startConnect() {
	console.log('- start connect');
	return new Promise(resolve => {
		setTimeout(async () => {
            await clickByLabel(document.querySelectorAll('button'), 'Launch', 5000);
			await clickByLabel(document.querySelectorAll('button'), 'Confirm', 5000);
            await clickByLabel(document.querySelectorAll('button'), "Connect", 5000, true);
            await clickByLabel(document.querySelectorAll('button'), "Back to Tomarket");
            
            //click button "Back to Hamster Kombat" is not work: fixed by below code
            let iframeList = document.querySelectorAll('div.popup-payment-verification');
            console.log('- iframeList length:', iframeList.length);
            if(iframeList.length >= 2) {
                //iframe connect
                iframeList[1].classList.add('hide');
            }
            if(iframeList.length >= 3) {
                //iframe back to game
                iframeList[2].classList.add('hide');
            }
            resolve();
		}, 2000);
	});
}


async function checkExistElm(elmList, label, time = 0) {
	let result = false;
	if (elmList.length && label) {
		for (let btnItem of elmList) {
			if(btnItem.textContent.includes(label)){
                console.log('--- elm exist', btnItem);
                result = true;
				break;
			}
		}
	}
	return new Promise(resolve => setTimeout(resolve(result), time));
}

async function simulateMouseClick(el) {
  let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
  el.dispatchEvent(new MouseEvent("mousedown", opts));
  await new Promise(r => setTimeout(r, 50));
  el.dispatchEvent(new MouseEvent("mouseup", opts));
  el.dispatchEvent(new MouseEvent("click", opts));
}

//For React ≥ 15.6.1
async function simulateMouseInput(el, value) {
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
      window.HTMLInputElement.prototype,
      'value').set;
    nativeInputValueSetter.call(el, value);
    const event = new Event('input', { bubbles: true });
    el.dispatchEvent(event);
}

async function waitClick(btn, time = 1000) {
	if (btn) await simulateMouseClick(btn);
	return new Promise(resolve => setTimeout(resolve, time));
}
async function clickByLabel(btn_list, label, time = 1000, must_same = false) {
    let isElement =  false;
	if (btn_list.length && label) {
        for await (const btnItem of btn_list) {
            //console.log('--', btnItem.textContent, btnItem);
            if((!must_same && btnItem.textContent.includes(label)) || (must_same && btnItem.textContent == label)) {
                console.log('->', btnItem.textContent, btnItem);
                await simulateMouseClick(btnItem);
                isElement = true;
                // break;
			}
        }
	}
	return new Promise(resolve => setTimeout(resolve, isElement ? time : 1000));
}
        """
SCRIPT_GAME_HAMTER = """
        (async function () {
            setInterval(() => {
                if(document.querySelector('.season-end-bottom-inner')){
                    document.querySelector('.season-end-bottom-inner button').click()
                }
                if(document.querySelector('.slider-onb-next')){
                    document.querySelector('.slider-onb-next').click()
                }
                if(document.querySelector('.slider-onb-button button')){
                    document.querySelector('.slider-onb-button button').click()
                }
                if(document.querySelector('.user-tap-button')){
                    document.querySelector('.user-tap-button').click()
                }
                if(document.querySelector('.daily-reward-bottom-button')){
                    document.querySelector('.daily-reward-bottom-button button').click()
                }
                if(document.querySelector('.bottom-sheet-button ')){
                    document.querySelector('.bottom-sheet-button ').click()
                }
            }, 1000)
            
            await start();
        })();

        async function start() {
        	console.log('- start');
        	return new Promise(resolve => {
        		setTimeout(async () => {

                    await waitClick(document.querySelector('.achievements-show .bottom-sheet-close'), "Play", 1000, true);
                    await clickByLabel(document.querySelectorAll('.slider-onb-next'), "Next", 1000, true);
                    await clickByLabel(document.querySelectorAll('.slider-onb-next'), "Next", 1000, true);
                    await clickByLabel(document.querySelectorAll('.slider-onb-next'), "Next", 1000, true);
                    await clickByLabel(document.querySelectorAll('.slider-onb-next'), "Next", 1000, true);
                    await clickByLabel(document.querySelectorAll('button'), "Play", 2000, true);

        			//touch click button
        			await simulateMouseTouch(document.querySelector('button.user-tap-button'), 2000);
                    await clickByLabel(document.querySelectorAll('button'), "Play", 2000, true);
                    resolve();
        		}, 2000);
        	});
        }


        async function checkExistElm(elmList, label, time = 0) {
        	let result = false;
        	if (elmList.length && label) {
        		for (let btnItem of elmList) {
        			if(btnItem.textContent.includes(label)){
                        console.log('--- elm exist', btnItem);
                        result = true;
        				break;
        			}
        		}
        	}
        	return new Promise(resolve => setTimeout(resolve(result), time));
        }

        async function simulateMouseClick(el) {
          let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
          el.dispatchEvent(new MouseEvent("mousedown", opts));
          await new Promise(r => setTimeout(r, 50));
          el.dispatchEvent(new MouseEvent("mouseup", opts));
          el.dispatchEvent(new MouseEvent("click", opts));
        }

        async function simulateMouseTouch(el, time = 0) {
        	const evt1 = new PointerEvent('pointerdown', {clientX: 150, clientY: 300});
        	const evt2 = new PointerEvent('pointerup', {clientX: 150, clientY: 300});

        	el.dispatchEvent(evt1);
        	el.dispatchEvent(evt2);

            return new Promise(resolve => setTimeout(resolve, time));
        }


        //For React ≥ 15.6.1
        async function simulateMouseInput(el, value) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
              window.HTMLInputElement.prototype,
              'value').set;
            nativeInputValueSetter.call(el, value);
            const event = new Event('input', { bubbles: true });
            el.dispatchEvent(event);
        }

        async function waitClick(btn, time = 1000) {
        	if (btn) {
                console.log(btn);
                await simulateMouseClick(btn);
            }
        	return new Promise(resolve => setTimeout(resolve, time));
        }
        async function clickByLabel(btn_list, label, time = 1000, must_same = false) {
        	if (btn_list.length && label) {
                for await (const btnItem of btn_list) {
                    //console.log('--', btnItem.textContent, btnItem);
                    if((!must_same && btnItem.textContent.includes(label)) || (must_same && btnItem.textContent == label)) {
                        console.log('->', btnItem.textContent, btnItem);
                        await simulateMouseClick(btnItem);
                        break;
        			}
                }
        	}
        	return new Promise(resolve => setTimeout(resolve, time));
        }
                """
SCRIPT_TELE_CONTROL_START1 = """
        (async function () {
            await teleWallet1();
        })();

        async function teleWallet1() {
        	console.log('- teleWallet 1: init wallet');
        	return new Promise(resolve => {
        		setTimeout(async () => {
                    let openStartLoop = setInterval(async() => {
                        let startBtn = document.querySelector('button.chat-input-control-button');
                        if(startBtn) {
        					clearInterval(openStartLoop);
                            await waitClick(startBtn, 4000);                    

                            //open wallet
                            await clickByLabel(document.querySelectorAll('span.reply-markup-button-text'), 'Open Wallet');
                            await clickByLabel(document.querySelectorAll('span.checkbox-caption'), 'I agree to the');
                            await clickByLabel(document.querySelectorAll('button.popup-button'), 'Continue');
                            await clickByLabel(document.querySelectorAll('button.popup-button'), 'Launch', 2000);

        					resolve();
                        }
                    }, 1000);
        		}, 2000);
        	});
        }


        async function simulateMouseClick(el) {
          let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
          el.dispatchEvent(new MouseEvent("mousedown", opts));
          await new Promise(r => setTimeout(r, 50));
          el.dispatchEvent(new MouseEvent("mouseup", opts));
          el.dispatchEvent(new MouseEvent("click", opts));
        }

        //For React ≥ 15.6.1
        async function simulateMouseInput(el, value) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
              window.HTMLInputElement.prototype,
              'value').set;
            nativeInputValueSetter.call(el, value);
            const event = new Event('input', { bubbles: true });
            el.dispatchEvent(event);
        }

        async function waitClick(btn, time = 1000) {
        	if (btn) await simulateMouseClick(btn);
        	return new Promise(resolve => setTimeout(resolve, time));
        }
        async function clickByLabel(btnList, label, time = 1000) {
        	if (btnList.length && label) {
        		for (let btnItem of btnList) {
        			if(btnItem.textContent.includes(label)){
        				await simulateMouseClick(btnItem);
                        break;
        			}
        		}
        	}
        	return new Promise(resolve => setTimeout(resolve, time));
        }
                """
SCRIPT_WALLET_INIT1 = """
        (async function () {
            await walletInit1();
        })();

        async function walletInit1() {
        	console.log('- walletInit 1: click lets go');
        	return new Promise(resolve => {
        		setTimeout(async () => {
                    await clickByLabel(document.querySelectorAll('button'), "Let's go");
                    resolve();
        		}, 2000);
        	});
        }


        async function simulateMouseClick(el) {
          let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
          el.dispatchEvent(new MouseEvent("mousedown", opts));
          await new Promise(r => setTimeout(r, 50));
          el.dispatchEvent(new MouseEvent("mouseup", opts));
          el.dispatchEvent(new MouseEvent("click", opts));
        }

        //For React ≥ 15.6.1
        async function simulateMouseInput(el, value) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
              window.HTMLInputElement.prototype,
              'value').set;
            nativeInputValueSetter.call(el, value);
            const event = new Event('input', { bubbles: true });
            el.dispatchEvent(event);
        }

        async function waitClick(btn, time = 1000) {
        	if (btn) await simulateMouseClick(btn);
        	return new Promise(resolve => setTimeout(resolve, time));
        }
        async function clickByLabel(btnList, label, time = 1000) {
        	if (btnList.length && label) {
        		for (let btnItem of btnList) {
        			if(btnItem.textContent.includes(label)){
        				await simulateMouseClick(btnItem);
        			}
        		}
        	}
        	return new Promise(resolve => setTimeout(resolve, time));
        }
                """
SCRIPT_TELE_CONTROL_START2 = """
        (async function () {
            await teleWallet2();
        })();

        async function teleWallet2() {
        	console.log('- teleWallet 2: open setting page from telegram');
        	return new Promise(resolve => {
        		setTimeout(async () => {
                    await waitClick(document.querySelector('.popup-header button.btn-menu-toggle'));
                    await clickByLabel(document.querySelectorAll('.btn-menu-item span.btn-menu-item-text'), "Settings");

                    resolve();
        		}, 2000);
        	});
        }


        async function simulateMouseClick(el) {
          let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
          el.dispatchEvent(new MouseEvent("mousedown", opts));
          await new Promise(r => setTimeout(r, 50));
          el.dispatchEvent(new MouseEvent("mouseup", opts));
          el.dispatchEvent(new MouseEvent("click", opts));
        }

        //For React ≥ 15.6.1
        async function simulateMouseInput(el, value) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
              window.HTMLInputElement.prototype,
              'value').set;
            nativeInputValueSetter.call(el, value);
            const event = new Event('input', { bubbles: true });
            el.dispatchEvent(event);
        }

        async function waitClick(btn, time = 1000) {
        	if (btn) await simulateMouseClick(btn);
        	return new Promise(resolve => setTimeout(resolve, time));
        }
        async function clickByLabel(btnList, label, time = 1000) {
        	if (btnList.length && label) {
        		for (let btnItem of btnList) {
        			if(btnItem.textContent.includes(label)){
        				await simulateMouseClick(btnItem);
        			}
        		}
        	}
        	return new Promise(resolve => setTimeout(resolve, time));
        }
                """
SCRIPT_WALLET_INIT2 = """
        (async function () {
            await walletInit2();
        })();

        async function walletInit2() {
        	console.log('- walletInit 2: enable TON space + go to phrase page');
        	return new Promise(resolve => {
        		setTimeout(async () => {
                    //if wallet inited
                    /*let openTonSpace = document.querySelector('a[href="/scw/settings"]');
                    if(!openTonSpace) {

                    }*/

                    let isChecked = document.querySelector('input[type="checkbox"]').checked;

                    if(!isChecked) {
                        await clickByLabel(document.querySelectorAll('span'), "Show TON Space");
                    }
                    history.go(-1);

                    setTimeout(async () => {
                        await clickByLabel(document.querySelectorAll('span'), "TON Space");
                        await clickByLabel(document.querySelectorAll('div'), "Start Exploring TON", 6000);
                        //python get phrase key
                        await clickByLabel(document.querySelectorAll('div'), "Back Up Manually", 3000);
                        resolve();
                    }, 1000);
        		}, 2000);
        	});
        }


        async function simulateMouseClick(el) {
          let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
          el.dispatchEvent(new MouseEvent("mousedown", opts));
          await new Promise(r => setTimeout(r, 50));
          el.dispatchEvent(new MouseEvent("mouseup", opts));
          el.dispatchEvent(new MouseEvent("click", opts));
        }

        //For React ≥ 15.6.1
        async function simulateMouseInput(el, value) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
              window.HTMLInputElement.prototype,
              'value').set;
            nativeInputValueSetter.call(el, value);
            const event = new Event('input', { bubbles: true });
            el.dispatchEvent(event);
        }

        async function waitClick(btn, time = 1000) {
        	if (btn) await simulateMouseClick(btn);
        	return new Promise(resolve => setTimeout(resolve, time));
        }
        async function clickByLabel(btnList, label, time = 1000) {
        	if (btnList.length && label) {
        		for (let btnItem of btnList) {
        			if(btnItem.textContent.includes(label)){
        				await simulateMouseClick(btnItem);
        			}
        		}
        	}
        	return new Promise(resolve => setTimeout(resolve, time));
        }
                """
SCRIPT_TELE_CONTROL_START3 = """
        (async function () {
            await teleWallet3();
        })();

        async function teleWallet3() {
        	console.log('- teleWallet 3: click continue from telegram');
        	return new Promise(resolve => {
        		setTimeout(async () => {
                    await clickByLabel(document.querySelectorAll('.popup-footer button'), "Continue");                

                    resolve();
        		}, 2000);
        	});
        }


        async function simulateMouseClick(el) {
          let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
          el.dispatchEvent(new MouseEvent("mousedown", opts));
          await new Promise(r => setTimeout(r, 50));
          el.dispatchEvent(new MouseEvent("mouseup", opts));
          el.dispatchEvent(new MouseEvent("click", opts));
        }

        //For React ≥ 15.6.1
        async function simulateMouseInput(el, value) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
              window.HTMLInputElement.prototype,
              'value').set;
            nativeInputValueSetter.call(el, value);
            const event = new Event('input', { bubbles: true });
            el.dispatchEvent(event);
        }

        async function waitClick(btn, time = 1000) {
        	if (btn) await simulateMouseClick(btn);
        	return new Promise(resolve => setTimeout(resolve, time));
        }
        async function clickByLabel(btnList, label, time = 1000) {
        	if (btnList.length && label) {
        		for (let btnItem of btnList) {
        			if(btnItem.textContent.includes(label)){
        				await simulateMouseClick(btnItem);
        			}
        		}
        	}
        	return new Promise(resolve => setTimeout(resolve, time));
        }
                """
SCRIPT_WALLET_INIT3 = """
        (async function () {
            await walletInit3();
        })();

        async function walletInit3() {
            let phrase = '_PHRASE_KEY_';
        	console.log('- walletInit 3: verify phrase key: ', phrase);
        	return new Promise(resolve => {
        		setTimeout(async () => {
                    //verify phrase key
                    let phraseList = phrase.split(' ');
                    let inputs = document.querySelectorAll('input[type="text"]');
                    if(inputs.length) {
                        for(const inputItem of inputs) {
                            let phraseIndex = inputItem.getAttribute('aria-label').replace(':', '');
                            phraseIndex = parseInt(phraseIndex);
                            console.log('phraseIndex:', phraseIndex);
        					await simulateMouseInput(inputItem, phraseList[phraseIndex-1])
                        }    
                    }
                    resolve();
        		}, 2000);
        	});
        }


        async function simulateMouseClick(el) {
          let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
          el.dispatchEvent(new MouseEvent("mousedown", opts));
          await new Promise(r => setTimeout(r, 50));
          el.dispatchEvent(new MouseEvent("mouseup", opts));
          el.dispatchEvent(new MouseEvent("click", opts));
        }

        //For React ≥ 15.6.1
        async function simulateMouseInput(el, value) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
              window.HTMLInputElement.prototype,
              'value').set;
            nativeInputValueSetter.call(el, value);
            const event = new Event('input', { bubbles: true });
            el.dispatchEvent(event);
        }

        async function waitClick(btn, time = 1000) {
        	if (btn) await simulateMouseClick(btn);
        	return new Promise(resolve => setTimeout(resolve, time));
        }
        async function clickByLabel(btnList, label, time = 1000) {
        	if (btnList.length && label) {
        		for (let btnItem of btnList) {
        			if(btnItem.textContent.includes(label)){
        				await simulateMouseClick(btnItem);
        			}
        		}
        	}
        	return new Promise(resolve => setTimeout(resolve, time));
        }
                """
SCRIPT_TELE_CONTROL_START4 = """
        (async function () {
            await teleWallet4();
        })();

        async function teleWallet4() {
        	console.log('- teleWallet 4: click next from telegram');
        	return new Promise(resolve => {
        		setTimeout(async () => {
                    await clickByLabel(document.querySelectorAll('.popup-footer button'), "Next");                

                    resolve();
        		}, 2000);
        	});
        }


        async function simulateMouseClick(el) {
          let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
          el.dispatchEvent(new MouseEvent("mousedown", opts));
          await new Promise(r => setTimeout(r, 50));
          el.dispatchEvent(new MouseEvent("mouseup", opts));
          el.dispatchEvent(new MouseEvent("click", opts));
        }

        //For React ≥ 15.6.1
        async function simulateMouseInput(el, value) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
              window.HTMLInputElement.prototype,
              'value').set;
            nativeInputValueSetter.call(el, value);
            const event = new Event('input', { bubbles: true });
            el.dispatchEvent(event);
        }

        async function waitClick(btn, time = 1000) {
        	if (btn) await simulateMouseClick(btn);
        	return new Promise(resolve => setTimeout(resolve, time));
        }
        async function clickByLabel(btnList, label, time = 1000) {
        	if (btnList.length && label) {
        		for (let btnItem of btnList) {
        			if(btnItem.textContent.includes(label)){
        				await simulateMouseClick(btnItem);
        			}
        		}
        	}
        	return new Promise(resolve => setTimeout(resolve, time));
        }
                """
SCRIPT_WALLET_CLICK_TON = """
    (async function () {
            await walletGetPhrase();
            
            
        })();
        async function walletGetPhrase() { 
        	return new Promise(resolve => {
        		setTimeout(async () => {
                    await clickByLabel(document.querySelectorAll('span'), "Beta", 3000);
                    await clickByLabel(document.querySelectorAll('div'), "Tap to view phrase", 5000);
                    await clickByLabel(document.querySelectorAll('div'), "Copy Recovery Phrase", 5000);
                    
                    resolve();
        		}, 2000);
        	});
        }
        async function simulateMouseClick(el) {
          let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
          el.dispatchEvent(new MouseEvent("mousedown", opts));
          await new Promise(r => setTimeout(r, 50));
          el.dispatchEvent(new MouseEvent("mouseup", opts));
          el.dispatchEvent(new MouseEvent("click", opts));
        }

        //For React ≥ 15.6.1
        async function simulateMouseInput(el, value) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
              window.HTMLInputElement.prototype,
              'value').set;
            nativeInputValueSetter.call(el, value);
            const event = new Event('input', { bubbles: true });
            el.dispatchEvent(event);
        }

        async function waitClick(btn, time = 1000) {
        	if (btn) await simulateMouseClick(btn);
        	return new Promise(resolve => setTimeout(resolve, time));
        }
        async function clickByLabel(btnList, label, time = 1000) {
        	if (btnList.length && label) {
        		for (let btnItem of btnList) {
        			if(btnItem.textContent.includes(label)){
        				await simulateMouseClick(btnItem);
        			}
        		}
        	}
        	return new Promise(resolve => setTimeout(resolve, time));
        }
"""
SCRIPT_WALLET_INIT4 = """
        (async function () {
            await walletInit4();
        })();

        async function walletInit4() {
        	console.log('- walletInit 4: View TON Space');
        	return new Promise(resolve => {
        		setTimeout(async () => {
                    await clickByLabel(document.querySelectorAll('div'), "View TON Space");
                    // await clickByLabel(document.querySelectorAll('span'), "TON Space");
                    await clickByLabel(document.querySelectorAll('button'), "Deposit");
                    await clickByLabel(document.querySelectorAll('button'), "Show QR", 3000);
                    await clickByLabel(document.querySelectorAll('button'), "Copy Address", 2000);
                    resolve();
        		}, 2000);
        	});
        }


        async function simulateMouseClick(el) {
          let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
          el.dispatchEvent(new MouseEvent("mousedown", opts));
          await new Promise(r => setTimeout(r, 50));
          el.dispatchEvent(new MouseEvent("mouseup", opts));
          el.dispatchEvent(new MouseEvent("click", opts));
        }

        //For React ≥ 15.6.1
        async function simulateMouseInput(el, value) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
              window.HTMLInputElement.prototype,
              'value').set;
            nativeInputValueSetter.call(el, value);
            const event = new Event('input', { bubbles: true });
            el.dispatchEvent(event);
        }

        async function waitClick(btn, time = 1000) {
        	if (btn) await simulateMouseClick(btn);
        	return new Promise(resolve => setTimeout(resolve, time));
        }
        async function clickByLabel(btnList, label, time = 1000) {
        	if (btnList.length && label) {
        		for (let btnItem of btnList) {
        			if(btnItem.textContent.includes(label)){
        				await simulateMouseClick(btnItem);
        			}
        		}
        	}
        	return new Promise(resolve => setTimeout(resolve, time));
        }
                """
SCRIPT_GAME_WUKONG = """
        (async function () {
            await start();
        })();

        async function start() {
        	console.log('- start');
        	return new Promise(resolve => {
        		setTimeout(async () => {
                    let wHeight = window.innerHeight;
                    let wWidth = window.innerWidth;
                    let canvasButtonOptionInit = {clientX: Math.floor(wWidth/2), clientY: wHeight - 85};
                    let canvasButtonOptionClaim = {clientX: Math.floor(wWidth/2), clientY: window.innerHeight - Math.ceil((window.innerHeight/100)*24)
        }; //24% from bottom

                    //next + finish button
                    await waitClick(document.querySelector('#GameCanvas'), 2000, canvasButtonOptionInit);
                    await waitClick(document.querySelector('#GameCanvas'), 2000, canvasButtonOptionInit);
                    //claim button
                    await waitClick(document.querySelector('#GameCanvas'), 2000, canvasButtonOptionClaim);

                    resolve();
        		}, 1000);
        	});
        }


        async function checkExistElm(elmList, label, time = 0) {
        	let result = false;
        	if (elmList.length && label) {
        		for (let btnItem of elmList) {
        			if(btnItem.textContent.includes(label)){
                        console.log('--- elm exist', btnItem);
                        result = true;
        				break;
        			}
        		}
        	}
        	return new Promise(resolve => setTimeout(resolve(result), time));
        }

        async function simulateMouseClick(el, click_event_option = {}) {
          let opts = {
              ...click_event_option,
              view: window, bubbles: true, cancelable: true, buttons: 1
          };
          el.dispatchEvent(new MouseEvent("mousedown", opts));
          await new Promise(r => setTimeout(r, 50));
          el.dispatchEvent(new MouseEvent("mouseup", opts));
          el.dispatchEvent(new MouseEvent("click", opts));
        }

        async function simulateMouseTouch(el, time = 0) {
        	const evt1 = new PointerEvent('pointerdown', {clientX: 245, clientY: 700});
            const evt2 = new PointerEvent('pointerup', {clientX: 245, clientY: 700});

        	el.dispatchEvent(evt1);
        	el.dispatchEvent(evt2);

            return new Promise(resolve => setTimeout(resolve, time));
        }


        //For React ≥ 15.6.1
        async function simulateMouseInput(el, value) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
              window.HTMLInputElement.prototype,
              'value').set;
            nativeInputValueSetter.call(el, value);
            const event = new Event('input', { bubbles: true });
            el.dispatchEvent(event);
        }

        async function waitClick(btn, time = 1000, click_event_option) {
        	if (btn) {
                console.log(btn);
                await simulateMouseClick(btn, click_event_option);
            }
        	return new Promise(resolve => setTimeout(resolve, time));
        }
        async function clickByLabel(btn_list, label, time = 1000, must_same = false) {
        	if (btn_list.length && label) {
                for await (const btnItem of btn_list) {
                    //console.log('--', btnItem.textContent, btnItem);
                    if((!must_same && btnItem.textContent.includes(label)) || (must_same && btnItem.textContent == label)) {
                        console.log('->', btnItem.textContent, btnItem);
                        await simulateMouseClick(btnItem);
                        break;
        			}
                }
        	}
        	return new Promise(resolve => setTimeout(resolve, time));
        }
                """
SCRIPT_GAME_CAT = """
                (async function () {
                    await start();
                })();

                async function start() {
                	console.log('- start');
                	return new Promise(resolve => {
                		setTimeout(async () => {
                            await clickByLabel(document.querySelectorAll('button'), "Wow, let’s go!", 7000);

                            setTimeout(() => {
                                resolve();
                            }, 2000);
                		}, 2000);
                	});
                }

                async function waitClick(btn, time = 1000) {
                	if (btn) btn.click();
                	return new Promise(resolve => setTimeout(resolve, time));
                }
                async function clickByLabel(btnList, label, time = 1000) {
                	if (btnList.length && label) {
                		for (let btnItem of btnList) {
                			if(btnItem.textContent.includes(label)){
                				btnItem.click();
                			}
                		}
                	}
                	return new Promise(resolve => setTimeout(resolve, time));
                }
                        """
SCRIPT_GAME_BLUM = """
        (async function () {
            setInterval(() => {
                if(document.querySelector('.play-btn')){
                    document.querySelector('.play-btn').click()
                }

            }, 7000);
            
            await start();
        })();

        async function start() {
        	console.log('- start');
        	return new Promise(resolve => {
        		setTimeout(async () => {
                    await clickByLabel(document.querySelectorAll('.button-label'), "Claim", 2000);
                    await clickByLabel(document.querySelectorAll('button'), "Create account", 1000);
                    await clickByLabel(document.querySelectorAll('button'), "Continue");
                    await clickByLabel(document.querySelectorAll('button'), "Start farming");
                    await clickByLabel(document.querySelectorAll('.button-label'), "Claim", 2000);
                    setTimeout(() => {
                        resolve();
                    }, 2000);
        		}, 2000);
        	});
        }

        async function waitClick(btn, time = 1000) {
        	if (btn) btn.click();
        	return new Promise(resolve => setTimeout(resolve, time));
        }
        async function clickByLabel(btnList, label, time = 1000) {
        	if (btnList.length && label) {
        		for (let btnItem of btnList) {
        			if(btnItem.textContent.includes(label)){
        				btnItem.click();
        			}
        		}
        	}
        	return new Promise(resolve => setTimeout(resolve, time));
        }
                """
SCRIPT_GAME_TOMARKET = """
        (async function () {

            

            setInterval(() => { 
                if(document.querySelector('._buttonSmallBlue_wzwhq_176')){
                    document.querySelector('._buttonSmallBlue_wzwhq_176').click()
                }
            
            }, 2000)
            setInterval(() => { 
                if(document.querySelector('._stepState_12fgt_102')[1]){
                    document.querySelector('._stepState_12fgt_102')[1].click()
                }
            }, 10000)
             
            await start();

            await clickByLabel(document.querySelectorAll('p'), "FREE", 4000, true);

            setTimeout(() => { 
                document.querySelector('._tagStarLevel_1o98h_83').click()
                setTimeout(async () => {
                    
                    await clickByLabel(document.querySelectorAll('button'), "Reveal Your Level", 4000, true);
                    await clickByLabel(document.querySelectorAll('button'), "Reveal Your Level", 4000, true);
                    if(document.querySelector('._btn_1i45r_156')){
                        document.querySelector('._btn_1i45r_156').click()
                    }
                    await clickByLabel(document.querySelectorAll('button'), "Level Up", 3000, true);
                    await clickByLabel(document.querySelectorAll('button'), "Use", 3000, true);
                    setTimeout(() => { 
                        if(document.querySelector('._levelWrapper_17wjt_120')){
                            document.querySelector('._levelWrapper_17wjt_120').click()
                        }
                        
                        
                    }, 2000)
                }, 2000)
            }, 40000)
            
            setInterval(() => { 
                if(document.querySelector('._buttonSmallBlue_wzwhq_176')){
                    document.querySelector('._buttonSmallBlue_wzwhq_176').click()
                }
            
            }, 2000)
            
        })();
        async function start() {
        	console.log('- start');
        	return new Promise(resolve => {
        		setTimeout(async () => {
        		    await clickByLabel(document.querySelectorAll('div'), "View My Level", 2000);
                    await clickByLabel(document.querySelectorAll('div'), "Start earning TOMATO", 2000);
                    await clickByLabel(document.querySelectorAll('div'), "Continue", 2000);
                    setTimeout(() => {
                        resolve();
                    }, 2000);
        		}, 2000);
        	});
        }

        

        async function waitClick(btn, time = 1000) {
        	if (btn) btn.click();
        	return new Promise(resolve => setTimeout(resolve, time));
        }
        async function clickByLabel(btnList, label, time = 1000) {
        	if (btnList.length && label) {
        		for (let btnItem of btnList) {
        			if(btnItem.textContent.includes(label)){
        				btnItem.click();
        			}
        		}
        	}
        	return new Promise(resolve => setTimeout(resolve, time));
        }
"""
SCRIPT_GAME_START = """
    (async function () {
        await start();
    })();

    async function start() {
        console.log('- start');
        return new Promise(resolve => {
            setTimeout(async () => {
                
                await waitClick(document.querySelector('.new-message-bot-commands-view'), 2000);

                await clickByLabel(document.querySelectorAll('button'), 'Launch', 2000);
                await clickByLabel(document.querySelectorAll('button'), 'Confirm');

                setTimeout(() => {
                    resolve();
                }, 2000);
            }, 2000);
        });
    }



    async function checkExistElm(elmList, label, time = 0) {
        let result = false;
        if (elmList.length && label) {
            for (let btnItem of elmList) {
                if(btnItem.textContent.includes(label)){
                    console.log('--- elm exist', btnItem);
                    result = true;
                    break;
                }
            }
        }
        return new Promise(resolve => setTimeout(resolve(result), time));
    }

    async function simulateMouseClick(el) {
    let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
    el.dispatchEvent(new MouseEvent("mousedown", opts));
    await new Promise(r => setTimeout(r, 50));
    el.dispatchEvent(new MouseEvent("mouseup", opts));
    el.dispatchEvent(new MouseEvent("click", opts));
    }

    //For React ≥ 15.6.1
    async function simulateMouseInput(el, value) {
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
        window.HTMLInputElement.prototype,
        'value').set;
        nativeInputValueSetter.call(el, value);
        const event = new Event('input', { bubbles: true });
        el.dispatchEvent(event);
    }

    async function waitClick(btn, time = 1000) {
        if (btn) await simulateMouseClick(btn);
        return new Promise(resolve => setTimeout(resolve, time));
    }
    async function clickByLabel(btn_list, label, time = 1000, must_same = false) {
        if (btn_list.length && label) {
            for await (const btnItem of btn_list) {
                //console.log('--', btnItem.textContent, btnItem);
                if((!must_same && btnItem.textContent.includes(label)) || (must_same && btnItem.textContent == label)) {
                    //console.log('->', btnItem.textContent, btnItem);
                    await simulateMouseClick(btnItem);
                    break;
                }
            }
        }
        return new Promise(resolve => setTimeout(resolve, time));
    }
    """

SCRIPT_SET_NAME = """
       (async function () {
            await openSetUserNamePage();
        })();

        async function openSetUserNamePage() {
            console.log('- openSetUserNamePage');
            return new Promise(resolve => {
                setTimeout(async () => {
                    let openMenuLoop = setInterval(() => {
                        let ribbonMenu = document.querySelector('button[title="Open menu"]');
                        if(ribbonMenu) {
                            ribbonMenu.click();
                            clearInterval(openMenuLoop);

                            setTimeout(async () => {
                                //open setting page
                                await clickByLabel(document.querySelectorAll('div[role="menuitem"]'), 'Settings');
                            
                                setTimeout(async () => {
                                    //open profile page
                                    document.querySelector('button[title="Edit profile"]').click();
                                    await getUserName();
                                    //click save
                                    let saveBtn = document.querySelector('button[aria-label="Save"]');
                                    await simulateMouseClick(saveBtn);

                                    setTimeout(() => {
                                        resolve();
                                    }, 2000);
                                }, 1000);
                            }, 1000);
                        }
                    }, 500);
                }, 2000);
            });
        }

        async function getUserName() {
            console.log('- getUserName');
            return new Promise(resolve => {
                setTimeout(async () => {
                    let firstName = document.querySelector('input[aria-label="First name (required)"]').value;
                    let lastName = document.querySelector('input[aria-label="Last name (optional)"]').value;
                    let userNameInput =  document.querySelector('input[aria-label="Username"');
                    let userNameVal =  userNameInput.value;
                    
                    
                    let userName = firstName ? (firstName.toLowerCase() + '_' ): '';
                    userName += makeid(3);
                    userName += lastName ? lastName.toLowerCase() : '';
                    //remove number at start string
                    userName = userName.replace(/^\d{0,}/, '');
                    userName = userName.replace('🐾', '');
                    userName = userName.replace('🐾', '');
                    userName = userName.replace('🍅', '');
                    userName = userName.replace('🍅', '');
                    console.log('--- set username: ', userName);
                    if(!firstName.includes('🐾')){
                        document.querySelector('input[aria-label="First name (required)"]').value = firstName + '🐾';
                        await simulateMouseInput(document.querySelector('input[aria-label="First name (required)"]'));
                    }
                    if(!lastName.includes('🐾')){ 
                        document.querySelector('input[aria-label="Last name (optional)"]').value = lastName + '🐾';
                        await simulateMouseInput(document.querySelector('input[aria-label="Last name (optional)"]'));
                    }
                    
                    userNameInput.value = 'a' + userName + 'tu';
                    await simulateMouseInput(userNameInput);
                    
                    
                    setTimeout(() => {
                        resolve();
                    }, 3000);
                }, 2000);
            });
        }

        function makeid(length) {
            let result = '';
            const characters = 'abcdefghijklmnopqrstuvwxyz0123456789';
            const charactersLength = characters.length;
            let counter = 0;
            while (counter < length) {
            result += characters.charAt(Math.floor(Math.random() * charactersLength));
            counter += 1;
            }
            return result;
        }

        async function simulateMouseClick(el) {
        let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
        el.dispatchEvent(new MouseEvent("mousedown", opts));
        await new Promise(r => setTimeout(r, 50));
        el.dispatchEvent(new MouseEvent("mouseup", opts));
        el.dispatchEvent(new MouseEvent("click", opts));
        }

        async function simulateMouseInput(el) {
        let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
        el.dispatchEvent(new MouseEvent("mousedown", opts));
        await new Promise(r => setTimeout(r, 50));
        el.dispatchEvent(new MouseEvent("mouseup", opts));
        el.dispatchEvent(new MouseEvent("input", opts));
        }

        async function waitClick(btn, time = 1000) {
            if (btn) await simulateMouseClick(btn);
            return new Promise(resolve => setTimeout(resolve, time));
        }
        async function clickByLabel(btnList, label, time = 1000) {
            if (btnList.length && label) {
                for (let btnItem of btnList) {
                    if(btnItem.textContent.includes(label)){
                        await simulateMouseClick(btnItem);
                    }
                }
            }
            return new Promise(resolve => setTimeout(resolve, time));
        }
        """
SCRIPT_IFRAME_BYPASS_MOBILE = """
        let iframe = document.querySelector('iframe.payment-verification');
        if(iframe) {
            let src = iframe.getAttribute('src');
            src = src.replace("tgWebAppPlatform=weba", "tgWebAppPlatform=ios").replace("tgWebAppPlatform=web", "tgWebAppPlatform=ios")
            console.log('new src:', src);
            iframe.setAttribute('src', src);
        }
        """

SCRIPT_GAME_CONTROL = """
(async function () {
    await startGame();
})();

async function startGame() {
	console.log('- startGame');
	return new Promise(resolve => {
		setTimeout(async () => {
            await waitClick(document.querySelector('.tabs a[href="/wallet"]'));
            await clickByLabel(document.querySelectorAll('button'), "Connect wallet", 3000,true);
            await clickByLabel(document.querySelectorAll('button'), "Open Wallet in Telegram", 2000);
            await clickByLabel(document.querySelectorAll('button'), 'Launch');
            
            resolve();
		}, 2000);
	});
}


async function checkExistElm(elmList, label, time = 0) {
	let result = false;
	if (elmList.length && label) {
		for (let btnItem of elmList) {
			if(btnItem.textContent.includes(label)){
                console.log('--- elm exist', btnItem);
                result = true;
				break;
			}
		}
	}
	return new Promise(resolve => setTimeout(resolve(result), time));
}

async function simulateMouseClick(el) {
  let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
  el.dispatchEvent(new MouseEvent("mousedown", opts));
  await new Promise(r => setTimeout(r, 50));
  el.dispatchEvent(new MouseEvent("mouseup", opts));
  el.dispatchEvent(new MouseEvent("click", opts));
}

//For React ≥ 15.6.1
async function simulateMouseInput(el, value) {
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
      window.HTMLInputElement.prototype,
      'value').set;
    nativeInputValueSetter.call(el, value);
    const event = new Event('input', { bubbles: true });
    el.dispatchEvent(event);
}

async function waitClick(btn, time = 1000) {
	if (btn) await simulateMouseClick(btn);
	return new Promise(resolve => setTimeout(resolve, time));
}
async function clickByLabel(btn_list, label, time = 1000, must_same = false) {
	if (btn_list.length && label) {
        for await (const btnItem of btn_list) {
            //console.log('--', btnItem.textContent, btnItem);
            if((!must_same && btnItem.textContent.includes(label)) || (must_same && btnItem.textContent == label)) {
                //console.log('->', btnItem.textContent, btnItem);
                await simulateMouseClick(btnItem);
                break;
			}
        }
	}
	return new Promise(resolve => setTimeout(resolve, time));
}
        """

SCRIPT_WALLET_CONTROL = """
(async function () {
    await startConnect();
})();

async function startConnect() {
	console.log('- start connect');
	return new Promise(resolve => {
		setTimeout(async () => {

            await clickByLabel(document.querySelectorAll('button'), "Connect Wallet", 3000);
            await clickByLabel(document.querySelectorAll('button'), "Connect", 3000);

            //click button "Back to Hamster Kombat" is not work: fixed by below code
            let iframeList = document.querySelectorAll('div.popup-payment-verification');
            console.log('- iframeList length:', iframeList.length);
            if(iframeList.length >= 2) {
                //iframe connect
                iframeList[1].classList.add('hide');
            }
            if(iframeList.length >= 3) {
                //iframe back to game
                iframeList[2].classList.add('hide');
            }
            resolve();
		}, 2000);
	});
}


async function checkExistElm(elmList, label, time = 0) {
	let result = false;
	if (elmList.length && label) {
		for (let btnItem of elmList) {
			if(btnItem.textContent.includes(label)){
                console.log('--- elm exist', btnItem);
                result = true;
				break;
			}
		}
	}
	return new Promise(resolve => setTimeout(resolve(result), time));
}

async function simulateMouseClick(el) {
  let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
  el.dispatchEvent(new MouseEvent("mousedown", opts));
  await new Promise(r => setTimeout(r, 50));
  el.dispatchEvent(new MouseEvent("mouseup", opts));
  el.dispatchEvent(new MouseEvent("click", opts));
}

//For React ≥ 15.6.1
async function simulateMouseInput(el, value) {
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
      window.HTMLInputElement.prototype,
      'value').set;
    nativeInputValueSetter.call(el, value);
    const event = new Event('input', { bubbles: true });
    el.dispatchEvent(event);
}

async function waitClick(btn, time = 1000) {
	if (btn) await simulateMouseClick(btn);
	return new Promise(resolve => setTimeout(resolve, time));
}
async function clickByLabel(btn_list, label, time = 1000, must_same = false) {
	if (btn_list.length && label) {
        for await (const btnItem of btn_list) {
            //console.log('--', btnItem.textContent, btnItem);
            if((!must_same && btnItem.textContent.includes(label)) || (must_same && btnItem.textContent == label)) {
                console.log('->', btnItem.textContent, btnItem);
                await simulateMouseClick(btnItem);
                // break;
			}
        }
	}
	return new Promise(resolve => setTimeout(resolve, time));
}
        """

SCRIPT_GAME_SET_WALLET_DEFAULT = """
(async function () {
    await setDefaultWallet();
})();

async function setDefaultWallet() {
	console.log('- start setDefaultWallet');
	return new Promise(resolve => {
		setTimeout(async () => {
            await clickByLabel(document.querySelectorAll('button'), "Set as default withdrawal option", 3000, true);
            await clickByLabel(document.querySelectorAll('button'), "Thanks!");
            resolve();
		}, 2000);
	});
}


async function checkExistElm(elmList, label, time = 0) {
	let result = false;
	if (elmList.length && label) {
		for (let btnItem of elmList) {
			if(btnItem.textContent.includes(label)){
                console.log('--- elm exist', btnItem);
                result = true;
				break;
			}
		}
	}
	return new Promise(resolve => setTimeout(resolve(result), time));
}

async function simulateMouseClick(el) {
  let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
  el.dispatchEvent(new MouseEvent("mousedown", opts));
  await new Promise(r => setTimeout(r, 50));
  el.dispatchEvent(new MouseEvent("mouseup", opts));
  el.dispatchEvent(new MouseEvent("click", opts));
}

//For React ≥ 15.6.1
async function simulateMouseInput(el, value) {
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
      window.HTMLInputElement.prototype,
      'value').set;
    nativeInputValueSetter.call(el, value);
    const event = new Event('input', { bubbles: true });
    el.dispatchEvent(event);
}

async function waitClick(btn, time = 1000) {
	if (btn) await simulateMouseClick(btn);
	return new Promise(resolve => setTimeout(resolve, time));
}
async function clickByLabel(btn_list, label, time = 1000, must_same = false) {
	if (btn_list.length && label) {
        for await (const btnItem of btn_list) {
            //console.log('--', btnItem.textContent, btnItem);
            if((!must_same && btnItem.textContent.includes(label)) || (must_same && btnItem.textContent == label)) {
                console.log('->', btnItem.textContent, btnItem);
                await simulateMouseClick(btnItem);
                break;
			}
        }
	}
	return new Promise(resolve => setTimeout(resolve, time));
}
        """
SCRIPT_AUTO_NOTPIXEL = """
    setInterval(() => { 
        if(document.querySelector('._button_17fy4_1')) {
            document.querySelector('._button_17fy4_1').click()
        }
        if(document.querySelector('._button_13oyr_11')) {
            document.querySelector('._button_13oyr_11').click()
        }
    }, 4000)
"""

script_popup = f"""
            setInterval(() => {{
                if(document.querySelector('.popup-confirmation .checkbox-ripple')) {{
                    document.querySelector('.popup-confirmation .checkbox-ripple').click()
                    document.querySelector('.popup-confirmation .popup-button').click()
                }}
            }}, 5000)
            setInterval(() => {{
                        if(document.querySelector('.popup-footer button')) {{
                            var event = new Event('enable', {{ bubbles: true }});
                            document.querySelector('.popup-footer button').dispatchEvent(event);
                            document.querySelector('.popup-footer button').click()
                        }}
            }}, 10000)
        """
headers_tomarket = {
            "host": "api-web.tomarket.ai",
            "connection": "keep-alive",
            "accept": "application/json, text/plain, */*",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; Redmi 4A / 5A Build/QQ3A.200805.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.185 Mobile Safari/537.36",
            "content-type": "application/json",
            "origin": "https://mini-app.tomarket.ai",
            "x-requested-with": "tw.nekomimi.nekogram",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://mini-app.tomarket.ai/",
            "accept-language": "en-US,en;q=0.9",
        }
