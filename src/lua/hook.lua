local unpack = unpack or table.unpack

Hook = {}

Hook.FUNCTYPES = {
	BREAKPOINT = "__breakpoints",
	CALLBACK = "__callbacks",
	ONWRITE = "__onwrites",
	ONREAD = "__onreads",
}

local function _callfuncs(obj, which, ...)
	local _result = { ... }

	for i = 1, #obj[which], 1 do
		_result = { obj[which][i](unpack(_result)) }
	end

	if _result ~= nil and #_result > 0 then
		return unpack(_result)
	end
end

local function _inithook(obj)
	local typ = type(obj)

	-- Return if already initialized
	if typ == "table" and obj.__inithook then
		return obj
	end

	local hook = {}
	hook.__inithook = true
	hook.__breakpoints = {}
	hook.__callbacks = {}
	hook.__onreads = {}
	hook.__onwrites = {}
	hook.__orig = obj

	local _metatable = {}

	if typ == "function" then
		_metatable["__call"] = function(obj, ...)
			-- Call the breakpoints with original arguments
			local _r1 = { _callfuncs(hook, Hook.FUNCTYPES.BREAKPOINT, ...) }

			-- Call the original function with arguments modified by breakpoints OR
			-- with the original arguments if no modifications were made (no returns)
			local _r2 = (_r1 and #_r1 > 0 and { hook.__orig(unpack(_r1)) }) or { hook.__orig(...) }

			-- Call the callbacks with the return value of the original function OR
			-- with the original arguments if original function returned null
			local _r3 = (_r2 and #_r2 > 0 and { _callfuncs(hook, Hook.FUNCTYPES.CALLBACK, unpack(_r2)) })
				or { _callfuncs(hook, Hook.FUNCTYPES.CALLBACK, ...) }

			-- The final return value is the return value of the callbacks OR
			-- the return value of the original function if null
			local _result = (_r3 ~= nil and #_r3 > 0 and _r3) or _r2
			return unpack(_result)
		end
	end

	if typ == "table" then
		_metatable["__index"] = function(...)
			local _t, _k = ...
			-- Optionally return a new key to read from
			local _r = _callfuncs(hook, Hook.FUNCTYPES.ONREAD, ...)
			return (_r ~= nil and hook.__orig[_r]) or hook.__orig[_k]
		end

		_metatable["__newindex"] = function(...)
			local _t, _k, _v = ...
			-- Optionally return a new key and value to write
			local _r = { _callfuncs(hook, Hook.FUNCTYPES.ONWRITE, ...) }
			local _k1, _v1 = nil, nil
			if _r ~= nil and #_r > 0 then
				_k1, _v1 = unpack(_r)
				_k = _k1 or _k
				_v = _v1 or _v
			end
			hook.__orig[_k] = _v
		end
	end

	setmetatable(hook, _metatable)

	return hook
end

local function _addfunc(obj, which, func, ephemeral)
	if func == nil then
		return obj
	end
	obj = _inithook(obj)

	local _f_index = #obj[which] + 1

	obj[which][_f_index] = ephemeral
			and function(...)
				local _ret = func(...)
				if _ret == nil or _ret == true then
					obj = _clearfunc(obj, which, _f_index)
				end
				return _ret
			end
		or func

	return obj
end

function _clearfunc(obj, which, func_index)
	if obj == nil then
		return obj
	end
	obj[which][func_index] = nil
	return obj
end

function Hook.ishooked(obj)
	if type(obj) == "table" and obj.__inithook then
		return true
	end
	return false
end

function Hook.addbreakpoint(obj, func, ephemeral)
	return _addfunc(obj, Hook.FUNCTYPES.BREAKPOINT, func, ephemeral)
end

function Hook.addcallback(obj, func, ephemeral)
	return _addfunc(obj, Hook.FUNCTYPES.CALLBACK, func, ephemeral)
end

function Hook.addonread(obj, func, ephemeral)
	return _addfunc(obj, Hook.FUNCTYPES.ONREAD, func, ephemeral)
end

function Hook.addonwrite(obj, func, ephemeral)
	return _addfunc(obj, Hook.FUNCTYPES.ONWRITE, func, ephemeral)
end

function Hook.clear(obj)
	if Hook.ishooked(obj) then
		for i = 1, #Hook.FUNCTYPES, 1 do
			obj[Hook.FUNCTYPES[i]] = {}
		end
	end

	return obj.__orig
end

return Hook
